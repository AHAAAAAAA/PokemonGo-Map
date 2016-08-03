#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time

# Moved here so logger is configured at load time
logging.basicConfig(format='%(asctime)s [%(threadName)16s][%(module)14s][%(levelname)8s] %(message)s')
log = logging.getLogger()

from threading import Thread, Event
from queue import Queue
from flask_cors import CORS

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, insert_mock_data

from pogom.search import search_overseer_thread, fake_search_loop
from pogom.models import init_database, create_tables, drop_tables, Pokemon, Pokestop, Gym

from pogom.pgoapi.utilities import get_pos_by_name


if __name__ == '__main__':
    args = get_args()

    if args.debug:
        log.setLevel(logging.DEBUG);
    else:
        log.setLevel(logging.INFO);

    # Let's not forget to run Grunt / Only needed when running with webserver
    if not args.no_server:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'static/dist')):
            log.critical('Please run "grunt build" before starting the server');
            sys.exit();

    # These are very noisey, let's shush them up a bit
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('pogom.pgoapi.pgoapi').setLevel(logging.WARNING)
    logging.getLogger('pogom.pgoapi.rpc_api').setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    config['parse_pokemon'] = not args.no_pokemon
    config['parse_pokestops'] = not args.no_pokestops
    config['parse_gyms'] = not args.no_gyms

    # Turn these back up if debugging
    if args.debug:
        logging.getLogger('requests').setLevel(logging.DEBUG)
        logging.getLogger('pgoapi').setLevel(logging.DEBUG)
        logging.getLogger('rpc_api').setLevel(logging.DEBUG)


    position = get_pos_by_name(args.location)
    if not any(position):
        log.error('Could not get a position by name, aborting')
        sys.exit()

    log.info('Parsed location is: %.4f/%.4f/%.4f (lat/lng/alt)',
             position[0], position[1], position[2])

    if args.no_pokemon:
        log.info('Parsing of Pokemon disabled')
    if args.no_pokestops:
        log.info('Parsing of Pokestops disabled')
    if args.no_gyms:
        log.info('Parsing of Gyms disabled')

    config['LOCALE'] = args.locale
    config['CHINA'] = args.china

    app = Pogom(__name__)
    db = init_database(app)
    if args.clear_db:
        log.info('Clearing database')
        if args.db_type == 'mysql':
            drop_tables(db)
        elif os.path.isfile(args.db):
            os.remove(args.db)
    create_tables(db)

    app.set_current_location(position);

    # Control the search status (running or not) across threads
    pause_bit = Event()
    pause_bit.clear()

    # Setup the location tracking queue and push the first location on
    new_location_queue = Queue()
    new_location_queue.put(position)

    if not args.only_server:
        # Gather the pokemons!
        if not args.mock:
            log.debug('Starting a real search thread')
            search_thread = Thread(target=search_overseer_thread, args=(args, new_location_queue, pause_bit))
        else:
            log.debug('Starting a fake search thread')
            insert_mock_data(position)
            search_thread = Thread(target=fake_search_loop)

        search_thread.daemon = True
        search_thread.name = 'search_thread'
        search_thread.start()

    if args.cors:
        CORS(app);

    app.set_search_control(pause_bit)
    app.set_location_queue(new_location_queue)

    config['ROOT_PATH'] = app.root_path
    config['GMAPS_KEY'] = args.gmaps_key
    config['REQ_SLEEP'] = args.scan_delay

    if args.no_server:
        # This loop allows for ctrl-c interupts to work since flask won't be holding the program open
        while search_thread.is_alive():
            time.sleep(60)
    else:
        app.run(threaded=True, use_reloader=False, debug=args.debug, host=args.host, port=args.port)
