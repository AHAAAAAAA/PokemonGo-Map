#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from datetime import datetime

from . import config
from .models import Pokemon, Gym, Pokestop


class Pogom(Flask):
    def __init__(self, import_name, **kwargs):
        super(Pogom, self).__init__(import_name, **kwargs)
        self.json_encoder = CustomJSONEncoder
        self.route("/", methods=['GET'])(self.fullmap)
        self.route("/pokemons/<stamp>", methods=['GET'])(self.pokemons)
        self.route("/pokemons", methods=['GET'])(self.pokemons_all)
        self.route("/gyms", methods=['GET'])(self.gyms)
        self.route("/pokestops", methods=['GET'])(self.pokestops)
        self.route("/raw_data/<stamp>", methods=['GET'])(self.raw_data)
        self.route("/next_loc", methods=['POST'])(self.next_loc)

    def fullmap(self):
        return render_template('map.html',
                               lat=config['ORIGINAL_LATITUDE'],
                               lng=config['ORIGINAL_LONGITUDE'],
                               gmaps_key=config['GMAPS_KEY'])

    def raw_data(self, stamp):
        return jsonify({
            'gyms': [g for g in Gym.get()],
            'pokestops': [p for p in Pokestop.get()],
            'pokemons': Pokemon.get_active(stamp)
        })

    def pokemons(self, stamp):
        return jsonify(Pokemon.get_active(stamp))

    def pokemons_all(self):
        return jsonify(Pokemon.get_active(None))

    def pokestops(self):
        return jsonify([p for p in Pokestop.get()])


    def gyms(self):
        return jsonify([g for g in Gym.select().dicts()])


    def next_loc(self):
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        if not (lat and lon):
            print('[-] Invalid next location: %s,%s' % (lat, lon))
            return 'bad parameters', 400
        else:
            config['ORIGINAL_LATITUDE'] = lat
            config['ORIGINAL_LONGITUDE'] = lon
            return 'ok'


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
