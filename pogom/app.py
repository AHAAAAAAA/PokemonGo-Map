#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
from flask import Flask, jsonify, render_template
from flask.json import JSONEncoder
from datetime import datetime

from . import config
from .models import Pokemon, Gym, Pokestop


class Pogom(Flask):
    def __init__(self, name):
        super(Pogom, self).__init__(name)
        self.json_encoder = CustomJSONEncoder
        self.route("/", methods=['GET'])(self.fullmap)
        self.route("/pokemons", methods=['GET'])(self.pokemons)
        self.route("/gyms", methods=['GET'])(self.gyms)
        self.route("/pokestops", methods=['GET'])(self.pokestops)

    def fullmap(self):
        return render_template('map.html',
                               lat=config['ORIGINAL_LATITUDE'],
                               lng=config['ORIGINAL_LONGITUDE'],
                               gmaps_key=config['GMAPS_KEY'])

    def pokemons(self):
        return jsonify(Pokemon.get_active(ignore=config['IGNORE'],
                                          only=config['ONLY']))

    def pokestops(self):
        return jsonify([p for p in Pokestop.select().dicts()])

    def gyms(self):
        return jsonify([g for g in Gym.select().dicts()])


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
