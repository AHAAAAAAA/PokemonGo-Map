#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time

from threading import Thread
from flask_cors import CORS, cross_origin

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, insert_mock_data, get_old_gmaps_key
from pogom.search import search_loop, create_search_threads
from pogom.models import init_database, create_tables, Pokemon, Pokestop, Gym

from pogom.pgoapi.utilities import get_pos_by_name

from pogom.exceptions import APIKeyException

log = logging.getLogger(__name__)

search_thread = Thread()

def start_locator_thread(args):
    search_thread = Thread(target=search_loop, args=(args,))
    search_thread.daemon = True
    search_thread.name = 'search_thread'
    search_thread.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')

    logging.getLogger("peewee").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    args = get_args()

    if not args.searcher and not args.server:
        print sys.argv[0] + ': error: Turning off the server and search is silly, nothing would run!'
        sys.exit(1);

    config['parse_pokemon'] = not args.no_pokemon
    config['parse_pokestops'] = not args.no_pokestops
    config['parse_gyms'] = not args.no_gyms

    if args.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)

    db = init_database()
    create_tables(db)

    position = get_pos_by_name(args.location)
    if not any(position):
        log.error('Could not get a position by name, aborting.')
        sys.exit()

    log.info('Parsed location is: {:.4f}/{:.4f}/{:.4f} (lat/lng/alt)'.
             format(*position))
    if args.no_pokemon:
        log.info('Parsing of Pokemon disabled.')
    if args.no_pokestops:
        log.info('Parsing of Pokestops disabled.')
    if args.no_gyms:
        log.info('Parsing of Gyms disabled.')

    config['ORIGINAL_LATITUDE'] = position[0]
    config['ORIGINAL_LONGITUDE'] = position[1]
    config['LOCALE'] = args.locale
    config['CHINA'] = args.china

    # Start the searcher, if enabled
    if args.searcher:
        create_search_threads(args.num_threads)
        if not args.mock:
            start_locator_thread(args)
        else:
            insert_mock_data()

        # If the server isn't going to be on, we should just loop here
        if not args.server:
            while not search_thread.isAlive():
                time.sleep(1)
            search_thread.join()

    # Start the web application, if enabled
    if args.server:
        # Load the gmaps key from command line, ini file, or even the old json file
        if args.gmaps_key is not None:
            config['GMAPS_KEY'] = args.gmaps_key
        else:
            config['GMAPS_KEY'] = get_old_gmaps_key()

        # If the key wasn't present, we can't continue
        if config['GMAPS_KEY'] == "":
            raise APIKeyException(\
                "No Google Maps Javascript API key in \config\config.ini!"
                " Please take a look at the wiki for instructions on how to"
                " generate this key, then add that key to the file.")

        app = Pogom(__name__)

        if args.cors:
            CORS(app);

        config['ROOT_PATH'] = app.root_path

        if args.ssl_key != "" and args.ssl_cert != "":
            ssl_context=(args.ssl_cert, args.ssl_key)
        else:
            ssl_context=None

        app.run(threaded=True, debug=args.debug, host=args.host, port=args.port, ssl_context=ssl_context)
