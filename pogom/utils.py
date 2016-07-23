#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getpass
import argparse
import re
import uuid
import os
import json
from datetime import datetime, timedelta
import ConfigParser

from . import config
from exceptions import APIKeyException


def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string

def parse_config(args):
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(os.path.dirname(__file__), '../config/config.ini'))
    args.auth_service = Config.get('Authentication', 'Service')
    args.username = Config.get('Authentication', 'Username')
    args.password = Config.get('Authentication', 'Password')
    args.location = Config.get('Search_Settings', 'Location')
    args.step_limit = int(Config.get('Search_Settings', 'Steps'))
    args.scan_delay = int(Config.get('Search_Settings', 'Scan_delay'))
    if Config.get('Misc', 'Google_Maps_API_Key') :
        args.gmaps_key = Config.get('Misc', 'Google_Maps_API_Key') 
    args.host = Config.get('Misc', 'Host') 
    args.port = Config.get('Misc', 'Port') 
    return args

def get_args():
    # fuck PEP8
    parser = argparse.ArgumentParser()
    parser.add_argument('-se', '--settings',action='store_true',default=False)
    parser.add_argument('-a', '--auth-service', type=str.lower, help='Auth Service', default='ptc')
    parser.add_argument('-u', '--username', help='Username', required=False)
    parser.add_argument('-p', '--password', help='Password', required=False)
    parser.add_argument('-l', '--location', type=parse_unicode, help='Location, can be an address or coordinates', required=False)
    parser.add_argument('-st', '--step-limit', help='Steps', required=False, type=int)
    parser.add_argument('-sd', '--scan-delay', help='Time delay before beginning new scan', required=False, type=int, default=1)
    parser.add_argument('-dc','--display-in-console',help='Display Found Pokemon in Console',action='store_true',default=False)
    parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=5000)
    parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check'
                        'locale folder for more options', default='en')
    parser.add_argument('-c', '--china', help='Coordinates transformer for China', action='store_true')
    parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true')
    parser.add_argument('-m', '--mock', help='Mock mode. Starts the web server but not the background thread.', action='store_true', default=False)
    parser.add_argument('-ns', '--no-server', help='No-Server Mode. Starts the searcher but not the Webserver.', action='store_true', default=False, dest='no_server')
    parser.add_argument('-k', '--google-maps-key', help='Google Maps Javascript API Key', default=None, dest='gmaps_key')
    parser.add_argument('-C', '--cors', help='Enable CORS on web server', action='store_true', default=False)
    parser.add_argument('-D', '--db', help='Database filename', default='pogom.db')
    parser.add_argument('-t', '--threads', help='Number of search threads', required=False, type=int, default=5, dest='num_threads')
    parser.set_defaults(DEBUG=False)
    args = parser.parse_args()

    if (args.settings):
        args = parse_config(args) 
    else:
        if (args.username is None or args.location is None or args.step_limit is None):
            parser.print_usage()
            print sys.argv[0] + ': error: arguments -u/--username, -l/--location, -st/--step-limit are required'
            sys.exit(1);

        if args.password is None:
            args.password = getpass.getpass()

    return args

def insert_mock_data():
    num_pokemon = 6
    num_pokestop = 6
    num_gym = 6

    from .models import Pokemon, Pokestop, Gym
    from .search import generate_location_steps

    latitude, longitude = float(config['ORIGINAL_LATITUDE']), float(config['ORIGINAL_LONGITUDE'])

    locations = [l for l in generate_location_steps((latitude, longitude), num_pokemon)]
    disappear_time = datetime.now() + timedelta(hours=1)

    detect_time = datetime.now()

    for i in xrange(num_pokemon):
        Pokemon.create(encounter_id=uuid.uuid4(),
                       spawnpoint_id='sp{}'.format(i),
                       pokemon_id=(i+1) % 150,
                       latitude=locations[i][0],
                       longitude=locations[i][1],
                       disappear_time=disappear_time,
                       detect_time=detect_time)

    for i in range(num_pokestop):

        Pokestop.create(pokestop_id=uuid.uuid4(),
                        enabled=True,
                        latitude=locations[i+num_pokemon][0],
                        longitude=locations[i+num_pokemon][1],
                        last_modified=datetime.now(),
                        #Every other pokestop be lured
                        lure_expiration=disappear_time if (i % 2 == 0) else None
                        )

    for i in range(num_gym):
        Gym.create(gym_id=uuid.uuid4(),
                   team_id=i % 3,
                   guard_pokemon_id=(i+1) % 150,
                   latitude=locations[i + num_pokemon + num_pokestop][0],
                   longitude=locations[i + num_pokemon + num_pokestop][1],
                   last_modified=datetime.now(),
                   enabled=True,
                   gym_points=1000
                   )

def get_pokemon_name(pokemon_id):
    if not hasattr(get_pokemon_name, 'names'):
        file_path = os.path.join(
            config['ROOT_PATH'],
            config['LOCALES_DIR'],
            'pokemon.{}.json'.format(config['LOCALE']))

        with open(file_path, 'r') as f:
            get_pokemon_name.names = json.loads(f.read())

    return get_pokemon_name.names[str(pokemon_id)]

def load_credentials(filepath):
    try:
        with open(filepath+os.path.sep+'/config/credentials.json') as file:
            creds = json.load(file)
    except IOError:
        creds = {}
    if not creds.get('gmaps_key'):
        raise APIKeyException(\
            "No Google Maps Javascript API key entered in \config\credentials.json file!"
            " Please take a look at the wiki for instructions on how to generate this key,"
            " then add that key to the file!")
    return creds
