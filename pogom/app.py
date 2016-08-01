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
