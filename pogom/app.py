#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import logging

from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from flask_compress import Compress
from datetime import datetime
from s2sphere import *
from pogom.utils import get_args
from datetime import timedelta
from collections import OrderedDict

from . import config
from .models import Pokemon, Gym, Pokestop, ScannedLocation

log = logging.getLogger(__name__)
compress = Compress()


class Pogom(Flask):
    def __init__(self, import_name, **kwargs):
        super(Pogom, self).__init__(import_name, **kwargs)
        compress.init_app(self)
        self.json_encoder = CustomJSONEncoder
        self.route("/", methods=['GET'])(self.fullmap)
        self.route("/raw_data", methods=['GET'])(self.raw_data)
        self.route("/loc", methods=['GET'])(self.loc)
        self.route("/next_loc", methods=['POST'])(self.next_loc)
        self.route("/mobile", methods=['GET'])(self.list_pokemon)
        self.route("/search_control", methods=['GET'])(self.get_search_control)
        self.route("/search_control", methods=['POST'])(self.post_search_control)
        self.route("/stats", methods=['GET'])(self.get_stats)

    def set_search_control(self, control):
        self.search_control = control

    def set_location_queue(self, queue):
        self.location_queue = queue

    def set_current_location(self, location):
        self.current_location = location

    def get_search_control(self):
        return jsonify({'status': not self.search_control.is_set()})

    def post_search_control(self):
        args = get_args()
        if not args.search_control:
            return 'Search control is disabled', 403
        action = request.args.get('action','none')
        if action == 'on':
            self.search_control.clear()
            log.info('Search thread resumed')
        elif action == 'off':
            self.search_control.set()
            log.info('Search thread paused')
        else:
            return jsonify({'message':'invalid use of api'})
        return self.get_search_control()

    def fullmap(self):
        args = get_args()
        fixed_display = "none" if args.fixed_location else "inline"
        search_display = "inline" if args.search_control else "none"

        return render_template('map.html',
                               lat=self.current_location[0],
                               lng=self.current_location[1],
                               gmaps_key=config['GMAPS_KEY'],
                               lang=config['LOCALE'],
                               is_fixed=fixed_display,
                               search_control=search_display
                               )

    def raw_data(self):
        d = {}
        swLat = request.args.get('swLat')
        swLng = request.args.get('swLng')
        neLat = request.args.get('neLat')
        neLng = request.args.get('neLng')
        if request.args.get('pokemon', 'true') == 'true':
            if request.args.get('ids'):
                ids = [int(x) for x in request.args.get('ids').split(',')]
                d['pokemons'] = Pokemon.get_active_by_id(ids, swLat, swLng,
                                                         neLat, neLng)
            else:
                d['pokemons'] = Pokemon.get_active(swLat, swLng, neLat, neLng)

        if request.args.get('pokestops', 'false') == 'true':
            d['pokestops'] = Pokestop.get_stops(swLat, swLng, neLat, neLng)

        if request.args.get('gyms', 'true') == 'true':
            d['gyms'] = Gym.get_gyms(swLat, swLng, neLat, neLng)

        if request.args.get('scanned', 'true') == 'true':
            d['scanned'] = ScannedLocation.get_recent(swLat, swLng, neLat,
                                                      neLng)

        if request.args.get('seen', 'false') == 'true':
            for duration in self.get_valid_stat_input()["duration"]["items"].values():
                if duration["selected"] == "SELECTED":
                    d['seen'] = Pokemon.get_seen(duration["value"])
                    break

        if request.args.get('appearances', 'false') == 'true':
            d['appearances'] = Pokemon.get_appearances(request.args.get('pokemonid'), request.args.get('last', type=float))

        return jsonify(d)

    def loc(self):
        d = {}
        d['lat'] = self.current_location[0]
        d['lng'] = self.current_location[1]

        return jsonify(d)

    def next_loc(self):
        args = get_args()
        if args.fixed_location:
            return 'Location changes are turned off', 403
        # part of query string
        if request.args:
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
        # from post requests
        if request.form:
            lat = request.form.get('lat', type=float)
            lon = request.form.get('lon', type=float)

        if not (lat and lon):
            log.warning('Invalid next location: %s,%s', lat, lon)
            return 'bad parameters', 400
        else:
            self.location_queue.put((lat, lon, 0))
            self.set_current_location((lat, lon, 0))
            log.info('Changing next location: %s,%s', lat, lon)
            return 'ok'

    def list_pokemon(self):
        # todo: check if client is android/iOS/Desktop for geolink, currently
        # only supports android
        pokemon_list = []

        # Allow client to specify location
        lat = request.args.get('lat', self.current_location[0], type=float)
        lon = request.args.get('lon', self.current_location[1], type=float)
        origin_point = LatLng.from_degrees(lat, lon)

        for pokemon in Pokemon.get_active(None, None, None, None):
            pokemon_point = LatLng.from_degrees(pokemon['latitude'],
                                                pokemon['longitude'])
            diff = pokemon_point - origin_point
            diff_lat = diff.lat().degrees
            diff_lng = diff.lng().degrees
            direction = (('N' if diff_lat >= 0 else 'S')
                         if abs(diff_lat) > 1e-4 else '') +\
                        (('E' if diff_lng >= 0 else 'W')
                         if abs(diff_lng) > 1e-4 else '')
            entry = {
                'id': pokemon['pokemon_id'],
                'name': pokemon['pokemon_name'],
                'card_dir': direction,
                'distance': int(origin_point.get_distance(
                    pokemon_point).radians * 6366468.241830914),
                'time_to_disappear': '%d min %d sec' % (divmod((
                    pokemon['disappear_time']-datetime.utcnow()).seconds, 60)),
                'disappear_time': pokemon['disappear_time'],
                'disappear_sec': (pokemon['disappear_time']-datetime.utcnow()).seconds,
                'latitude': pokemon['latitude'],
                'longitude': pokemon['longitude']
            }
            pokemon_list.append((entry, entry['distance']))
        pokemon_list = [y[0] for y in sorted(pokemon_list, key=lambda x: x[1])]
        return render_template('mobile_list.html',
                               pokemon_list=pokemon_list,
                               origin_lat=lat,
                               origin_lng=lon)

    def get_valid_stat_input(self):
        duration = request.args.get("duration", type=str)
        sort = request.args.get("sort", type=str)
        order = request.args.get("order", type=str)
        valid_durations = OrderedDict()
        valid_durations["1h"] = {"display": "Last Hour", "value": timedelta(hours=1), "selected": ("SELECTED" if duration == "1h" else "")}
        valid_durations["3h"] = {"display": "Last 3 Hours", "value": timedelta(hours=3), "selected": ("SELECTED" if duration == "3h" else "")}
        valid_durations["6h"] = {"display": "Last 6 Hours", "value": timedelta(hours=6), "selected": ("SELECTED" if duration == "6h" else "")}
        valid_durations["12h"] = {"display": "Last 12 Hours", "value": timedelta(hours=12), "selected": ("SELECTED" if duration == "12h" else "")}
        valid_durations["1d"] = {"display": "Last Day", "value": timedelta(days=1), "selected": ("SELECTED" if duration == "1d" else "")}
        valid_durations["7d"] = {"display": "Last 7 Days", "value": timedelta(days=7), "selected": ("SELECTED" if duration == "7d" else "")}
        valid_durations["14d"] = {"display": "Last 14 Days", "value": timedelta(days=14), "selected": ("SELECTED" if duration == "14d" else "")}
        valid_durations["1m"] = {"display": "Last Month", "value": timedelta(days=365/12), "selected": ("SELECTED" if duration == "1m" else "")}
        valid_durations["3m"] = {"display": "Last 3 Months", "value": timedelta(days=3*365/12), "selected": ("SELECTED" if duration == "3m" else "")}
        valid_durations["6m"] = {"display": "Last 6 Months", "value": timedelta(days=6*365/12), "selected": ("SELECTED" if duration == "6m" else "")}
        valid_durations["1y"] = {"display": "Last Year", "value": timedelta(days=365), "selected": ("SELECTED" if duration == "1y" else "")}
        valid_durations["all"] = {"display": "Map Lifetime", "value": 0, "selected": ("SELECTED" if duration == "all" else "")}
        if duration not in valid_durations:
            valid_durations["1d"]["selected"] = "SELECTED"
        valid_sort = OrderedDict()
        valid_sort["count"] = {"display": "Count", "selected": ("SELECTED" if sort == "count" else "")}
        valid_sort["id"] = {"display": "Pokedex Number", "selected": ("SELECTED" if sort == "id" else "")}
        valid_sort["name"] = {"display": "Pokemon Name", "selected": ("SELECTED" if sort == "name" else "")}
        if sort not in valid_sort:
            valid_sort["count"]["selected"] = "SELECTED"
        valid_order = OrderedDict()
        valid_order["asc"] = {"display": "Ascending", "selected": ("SELECTED" if order == "asc" else "")}
        valid_order["desc"] = {"display": "Descending", "selected": ("SELECTED" if order == "desc" else "")}
        if order not in valid_order:
            valid_order["desc"]["selected"] = "SELECTED"
        valid_input = OrderedDict()
        valid_input["duration"] = {"display": "Duration", "items": valid_durations}
        valid_input["sort"] = {"display": "Sort", "items": valid_sort}
        valid_input["order"] = {"display": "Order", "items": valid_order}
        return valid_input

    def get_stats(self):
        return render_template('statistics.html',
                               lat=self.current_location[0],
                               lng=self.current_location[1],
                               gmaps_key=config['GMAPS_KEY'],
                               valid_input=self.get_valid_stat_input()
                               )


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
