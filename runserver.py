#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time

# Moved here so logger is configured at load time
logging.basicConfig(format='%(asctime)s [%(threadName)14s][%(module)14s] [%(levelname)7s] %(message)s')
log = logging.getLogger()

from threading import Thread
from flask_cors import CORS

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, insert_mock_data
from pogom.search import search_loop, create_search_threads, fake_search_loop
from pogom.search import search_loop_stop, search_loop_start
from pogom.models import init_database, create_tables, Pokemon, Pokestop, Gym

from pogom.pgoapi.utilities import get_pos_by_name


def main():
    global args
    args = get_args()

    if args.debug:
        log.setLevel(logging.DEBUG);
    else:
        log.setLevel(logging.INFO);

    # Let's not forget to run Grunt / Only needed when running with webserver
    if not args.no_server:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'static/dist')):
            log.critical('Please run "grunt build" before starting the server.');
            sys.exit();

    # These are very noisey, let's shush them up a bit
    logging.getLogger("peewee").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    config['parse_pokemon'] = not args.no_pokemon
    config['parse_pokestops'] = not args.no_pokestops
    config['parse_gyms'] = not args.no_gyms

    # Turn these back up if debugging
    if args.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)


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

    app = Pogom(__name__)
    db = init_database(app)
    if args.clear_db:
        if args.db_type == 'mysql':
            drop_tables(db)
        elif os.path.isfile(args.db):
            os.remove(args.db)
    create_tables(db)

    if not args.only_server:
        # Gather the pokemons!
        start_search_thread()

    app = Pogom(__name__)

    control = SearchControl()
    app.set_search_control(control)

    if args.cors:
        CORS(app);

    config['ROOT_PATH'] = app.root_path
    config['GMAPS_KEY'] = args.gmaps_key
    config['REQ_SLEEP'] = args.scan_delay

    if args.no_server:
        # This loop allows for ctrl-c interupts to work since flask won't be holding the program open
        while True:
            try:
                time.sleep(60)
            except:
                control.stop()
                break
    else:
        app.run(threaded=True, use_reloader=False, debug=args.debug, host=args.host, port=args.port)

#method to start (or restart the search thread)
def start_search_thread():
    global args
    global search_thread
    search_loop_start()
    if not args.mock:
        log.debug('(re)Starting a real search thread and {} search runner thread(s)'.format(args.num_threads))
        create_search_threads(args.num_threads)
        search_thread = Thread(target=search_loop, args=(args,))
    else:
        log.debug('(re)Starting a fake search thread')
        insert_mock_data()
        search_thread = Thread(target=fake_search_loop)

    search_thread.daemon = True
    search_thread.name = 'search_thread'
    search_thread.start()

#class to handle controlling the search threads
class SearchControl():
    def __init__(self):
        if args.search_control:
            self.state = 'searching'
        else:
            self.state = 'disabled'
        return
    def start(self):
        if self.state == 'searching' or self.state == 'disabled':
            return
        log.info('Start')
        start_search_thread()
        self.state = 'searching'
    def stop(self):
        if self.state == 'idle' or self.state == 'disabled':
            return
        log.info('Stop')
        search_loop_stop()
        self.state = 'idle'
    def status(self):
        return self.state

if __name__ == '__main__':
    main()
