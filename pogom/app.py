#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
from flask import Flask, jsonify, render_template
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
        self.route("/gyms/<stamp>", methods=['GET'])(self.gyms)
        self.route("/pokestops/<stamp>", methods=['GET'])(self.pokestops)
        self.route("/raw_data", methods=['GET'])(self.raw_data)

    def fullmap(self):
        return render_template('map.html',
                               lat=config['ORIGINAL_LATITUDE'],
                               lng=config['ORIGINAL_LONGITUDE'],
                               gmaps_key=config['GMAPS_KEY'])

    def get_raw_data(self, stamp):
        return {
            'gyms': [g for g in Gym.get()],
            'pokestops': [p for p in Pokestop.get()],
            'pokemons': Pokemon.get_active(stamp)
        }

    def raw_data(self, stamp):
        return jsonify(self.get_raw_data(stamp))

    def pokemons(self, stamp):
        return jsonify(self.get_raw_data(stamp)['pokemons'])

    def pokestops(self, stamp):
        return jsonify(self.get_raw_data(stamp)['pokestops'])

    def gyms(self, stamp):
        return jsonify(self.get_raw_data(stamp)['gyms'])




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
