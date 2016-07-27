#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getpass
import configargparse
import uuid
import os
import json
from datetime import datetime, timedelta
import logging
import shutil
import requests

from . import config

log = logging.getLogger(__name__)

def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string

def verify_config_file_exists(filename):
    fullpath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(fullpath) is False:
        log.info("Could not find " + filename + ", copying default")
        shutil.copy2(fullpath + '.example', fullpath)

def get_args():
    # fuck PEP8
    configpath = os.path.join(os.path.dirname(__file__), '../config/config.ini')
    parser = configargparse.ArgParser(default_config_files=[configpath])
    parser.add_argument('-a', '--auth-service', type=str.lower, help='Auth Service', default='ptc')
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('-l', '--location', type=parse_unicode, help='Location, can be an address or coordinates')
    parser.add_argument('-st', '--step-limit', help='Steps', type=int, default=12)
    parser.add_argument('-sd', '--scan-delay', help='Time delay between requests in scan threads', type=float, default=5)
    parser.add_argument('-td', '--thread-delay', help='Time delay between each scan thread loop', type=float, default=5)
    parser.add_argument('-ld', '--login-delay', help='Time delay between each login attempt', type=float, default=5)
    parser.add_argument('-dc', '--display-in-console',help='Display Found Pokemon in Console',action='store_true', default=False)
    parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=5000)
    parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check locale folder for more options', default='en')
    parser.add_argument('-c', '--china', help='Coordinates transformer for China', action='store_true')
    parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true')
    parser.add_argument('-m', '--mock', help='Mock mode. Starts the web server but not the background thread.', action='store_true', default=False)
    parser.add_argument('-ns', '--no-server', help='No-Server Mode. Starts the searcher but not the Webserver.', action='store_true', default=False)
    parser.add_argument('-os', '--only-server', help='Server-Only Mode. Starts only the Webserver without the searcher.', action='store_true', default=False)
    parser.add_argument('-fl', '--fixed-location', help='Hides the search bar for use in shared maps.', action='store_true', default=False)
    parser.add_argument('-k', '--gmaps-key', help='Google Maps Javascript API Key', required=True)
    parser.add_argument('-C', '--cors', help='Enable CORS on web server', action='store_true', default=False)
    parser.add_argument('-D', '--db', help='Database filename', default='pogom.db')
    parser.add_argument('-t', '--num-threads', help='Number of search threads', type=int, default=1)
    parser.add_argument('-np', '--no-pokemon', help='Disables Pokemon from the map (including parsing them into local db)', action='store_true', default=False)
    parser.add_argument('-ng', '--no-gyms', help='Disables Gyms from the map (including parsing them into local db)', action='store_true', default=False)
    parser.add_argument('-nk', '--no-pokestops', help='Disables PokeStops from the map (including parsing them into local db)', action='store_true', default=False)
    parser.add_argument('--db-type', help='Type of database to be used (default: sqlite)', default='sqlite')
    parser.add_argument('--db-name', help='Name of the database to be used')
    parser.add_argument('--db-user', help='Username for the database')
    parser.add_argument('--db-pass', help='Password for the database')
    parser.add_argument('--db-host', help='IP or hostname for the database')
    parser.add_argument('-wh', '--webhook', help='Define URL(s) to POST webhook information to', nargs='*', default=False, dest='webhooks')
    parser.set_defaults(DEBUG=False)

    args = parser.parse_args()

    if args.only_server:
        if args.location is None:
            parser.print_usage()
            print sys.argv[0] + ': error: arguments -l/--location is required'
            sys.exit(1);
    else:
        if (args.username is None or args.location is None or args.step_limit is None):
            parser.print_usage()
            print sys.argv[0] + ': error: arguments -u/--username, -l/--location, -st/--step-limit are required'
            sys.exit(1);

        if config["PASSWORD"] is None and args.password is None:
            config["PASSWORD"] = args.password = getpass.getpass()
        elif args.password is None:
            args.password = config["PASSWORD"]

    return args

def insert_mock_data():
    num_pokemon = 6
    num_pokestop = 6
    num_gym = 6

    log.info('Creating fake: {} pokemon, {} pokestops, {} gyms'.format(
        num_pokemon, num_pokestop, num_gym))

    from .models import Pokemon, Pokestop, Gym
    from .search import generate_location_steps

    latitude, longitude = float(config['ORIGINAL_LATITUDE']), float(config['ORIGINAL_LONGITUDE'])

    locations = [l for l in generate_location_steps((latitude, longitude), num_pokemon)]
    disappear_time = datetime.now() + timedelta(hours=1)

    detect_time = datetime.now()

    for i in range(num_pokemon):
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
                        lure_expiration=disappear_time if (i % 2 == 0) else None,
                        active_pokemon_id=i
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

def send_to_webhook(message_type, message):
    args = get_args()

    data = {
        'type': message_type,
        'message': message
    }

    if args.webhooks:
        webhooks = args.webhooks

        for w in webhooks:
            try:
                requests.post(w, json=data, timeout=(None, 1))
            except requests.exceptions.ReadTimeout:
                log.debug('Could not receive response from webhook')
            except requests.exceptions.RequestException as e:
                log.debug(e)
