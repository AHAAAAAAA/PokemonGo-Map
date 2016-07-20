#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_googlemaps import icons
import json
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import config
import db

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

with open('credentials.json') as f:
    credentials = json.load(f)

with open('locales/pokemon.en.json') as f:
    pokemon_names = json.load(f)

GOOGLEMAPS_KEY = credentials.get('gmaps_key', None)

DEBUG = True
# VERBOSE_DEBUG = False  # if you want to write raw request/response to the console
# COORDS_LATITUDE = 0
# COORDS_LONGITUDE = 0
# COORDS_ALTITUDE = 0
# FLOAT_LAT = 0
# FLOAT_LONG = 0
# NEXT_LAT = 0
# NEXT_LONG = 0
origin_lat = (config.MAP_START[0] + config.MAP_END[0]) / 2.0
origin_lon = (config.MAP_START[1] + config.MAP_END[1]) / 2.0
auto_refresh = 0


def debug(message):
    if DEBUG:
        print '[-] {}'.format(message)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-H',
        '--host',
        help='Set web server listening host',
        default='127.0.0.1')
    parser.add_argument(
        '-P',
        '--port',
        type=int,
        help='Set web server listening port',
        default=5000)
    parser.add_argument(
        '-d', '--debug', help='Debug Mode', action='store_true')
    parser.set_defaults(DEBUG=True)
    return parser.parse_args()


def create_app():
    app = Flask(__name__, template_folder='templates')
    GoogleMaps(app, key=GOOGLEMAPS_KEY)
    return app


app = create_app()


@app.route('/data')
def data():
    """ Gets all the PokeMarkers via REST """
    return json.dumps(get_pokemarkers())


@app.route('/raw_data')
def raw_data():
    """ Gets raw data for pokemons/gyms/pokestops via REST """
    return flask.jsonify(pokemons=pokemons, gyms=gyms, pokestops=pokestops)


@app.route('/config')
def config():
    """ Gets the settings for the Google Maps via REST"""
    center = {
        'lat': FLOAT_LAT,
        'lng': FLOAT_LONG,
        'zoom': 15,
        'identifier': "fullmap"
    }
    return json.dumps(center)


@app.route('/')
def fullmap():
    return render_template(
        'example_fullmap.html',
        key=GOOGLEMAPS_KEY,
        fullmap=get_map(),
        auto_refresh=auto_refresh
    )


@app.route('/next_loc')
def next_loc():
    global NEXT_LAT, NEXT_LONG

    location_name = flask.request.args.get('name', '')
    if not location_name:
        return 'no location_name'
    # TODO:
    # coords = guess_coords(location_name)
    # NEXT_LAT = float(coords[0])
    # NEXT_LONG = float(coords[1])
    # print('[+] Saved next location as %s,%s' % (NEXT_LAT, NEXT_LONG))
    return 'ok'


@app.route('/gps')
def next_loc_gps():
    return render_template('nextloc_js.html')


def get_pokemarkers():
    markers = []
    session = db.Session()
    pokemons = db.get_sightings(session)

    for pokemon in pokemons:
        name = pokemon_names[pokemon.id]
        datestr = datetime.fromtimestamp(pokemon.expire_timestamp)
        dateoutput = datestr.strftime("%H:%M:%S")

        LABEL_TMPL = u'''
<div><b>{name}</b><span> - </span><small><a href='http://www.pokemon.com/us/pokedex/{id}' target='_blank' title='View in Pokedex'>#{id}</a></small></div>
<div>Disappears at - {disappear_time_formatted} <span class='label-countdown' disappears-at='{disappear_time}'></span></div>
<div><a href='https://www.google.com/maps/dir/Current+Location/{lat},{lng}' target='_blank' title='View in Maps'>Get Directions</a></div>
'''
        label = LABEL_TMPL.format(
            id=pokemon.id,
            name=name,
            disappear_time_formatted=dateoutput,
            lat=pokemon.lat,
            lng=pokemon.lon,
        )
        #  NOTE: `infobox` field doesn't render multiple line string in frontend
        label = label.replace('\n', '')

        markers.append({
            'type': 'pokemon',
            'name': name,
            'key': pokemon.id,
            'disappear_time': pokemon.expire_timestamp,
            'icon': 'static/icons/%d.png' % pokemon.id,
            'lat': pokemon.lat,
            'lng': pokemon.lon,
            'infobox': label
        })

    return markers


def get_map():
    fullmap = Map(
        identifier="fullmap2",
        style='height:100%;width:100%;top:0;left:0;position:absolute;z-index:200;',
        lat=origin_lat,
        lng=origin_lon,
        markers=get_pokemarkers(),
        zoom='15',
    )
    return fullmap


if __name__ == '__main__':
    args = get_args()
    app.run(debug=True, threaded=True, host=args.host, port=args.port)
