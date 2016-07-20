#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from datetime import datetime
import time
import logging
import threading

from . import config
from .models import Pokemon, Gym, Pokestop, ResponseResult
from .search import search_loop
from .utils import insert_mock_data

log = logging.getLogger(__name__)

class Pogom(Flask):

    # when initialized these should get pulled from initSearch
    args = None
    search_thread = None
    tStop = None

    def __init__(self, import_name, **kwargs):
        super(Pogom, self).__init__(import_name, **kwargs)
        self.json_encoder = CustomJSONEncoder
        self.route("/", methods=['GET'])(self.fullmap)
        self.route("/pokemons/<stamp>", methods=['GET'])(self.pokemons)
        self.route("/pokemons", methods=['GET'])(self.pokemons)
        self.route("/gyms", methods=['GET'])(self.gyms)
        self.route("/pokestops", methods=['GET'])(self.pokestops)
        self.route("/raw_data", methods=['GET'])(self.raw_data)
        self.route("/setLocation", methods=['POST'])(self.setLocation)

    def fullmap(self):
        return render_template('map.html',
                               lat=config['ORIGINAL_LATITUDE'],
                               lng=config['ORIGINAL_LONGITUDE'],
                               gmaps_key=config['GMAPS_KEY'])

    def get_raw_data(self, stamp):
         return {
             'gyms': [g for g in Gym.select().dicts()],
             'pokestops': [p for p in Pokestop.select().dicts()],
             'pokemons': Pokemon.get_active(stamp)
         }
    
    def pokemons(self):
        return jsonify(Pokemon.get_active())

    def pokestops(self):
        return jsonify([p for p in Pokestop.select().dicts()])
    
    def raw_data(self, stamp):
         return jsonify(self.get_raw_data(stamp))

    def gyms(self):
        return jsonify([g for g in Gym.select().dicts()])
    
    def pokemons(self, stamp):
         return jsonify(self.get_raw_data(stamp)['pokemons'])

    def pokestops(self, stamp):
         return jsonify(self.get_raw_data(stamp)['pokestops'])

    def gyms(self, stamp):
         return jsonify(self.get_raw_data(stamp)['gyms'])

    def setLocation(self):
        result = ResponseResult(request.data,'invalid request')
        if request.method == 'POST':
            
            result.resultMsg = 'lat {} lng {}'.format(request.form['lat'],request.form['lng'])
            log.info('got {}'.format(result.resultMsg))

            newLatitude = request.form['lat']
            newLongitude = request.form['lng']

            if (newLatitude and newLongitude):
                self.modify_locator_thread(newLatitude, newLongitude)
            else:
                result.resultMsg = 'no lat lng'
        return jsonify(result.serialize())
    
    ### SEARCH RELATED STUFF
    # locater thread is called once, which continues to loop
    # locater thread then runs an inner fuction, which continues forever, which pauses for 1 second
    # before executing search again

    def initSearch(self, args):
        log.info('init search...')
        #lets store this
        self.args = args

        if not args.mock:
            self.start_locator_thread()
        else:
            insert_mock_data(args.location, 6)
    
    def start_locator_thread(self):
        log.info('starting search thread...')
        self.tStop = threading.Event()
        self.search_thread = threading.Thread(target=search_loop, args=(self.args, self.tStop,))
        self.search_thread.daemon = True
        self.search_thread.name = 'search_thread'
        self.search_thread.start()

    def interrupt(self):
        log.info('cancelling current thread...')
        self.tStop.set()

    def modify_locator_thread(self, lat, lng):
        #cancel the current thread
        self.interrupt()

        #TODO: we should probably wait till the search_thread is done?
        while self.search_thread.is_alive():
            time.sleep(.25)
            #wait for thread to cancel

       	config['ORIGINAL_LATITUDE'] = float(lat)
        config['ORIGINAL_LONGITUDE'] = float(lng)
        #restart the search threads
        self.start_locator_thread()

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
