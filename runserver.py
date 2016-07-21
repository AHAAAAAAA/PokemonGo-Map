#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

from threading import Thread

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, insert_mock_data, load_credentials
from pogom.search import search_loop
from pogom.models import create_tables, Pokemon, Pokestop, Gym

from pogom.pgoapi.utilities import get_pos_by_name

log = logging.getLogger(__name__)


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

    args = get_args()

    if args.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)

    create_tables()

    position = get_pos_by_name(args.location)
    log.info('Parsed location is: {:.4f}/{:.4f}/{:.4f} (lat/lng/alt)'.
             format(*position))

    config['ORIGINAL_LATITUDE'] = position[0]
    config['ORIGINAL_LONGITUDE'] = position[1]
    config['LOCALE'] = args.locale

    if args.ignore:
        Pokemon.IGNORE = [i.lower().strip() for i in args.ignore.split(',')]
    elif args.only:
        Pokemon.ONLY = [i.lower().strip() for i in args.only.split(',')]

    if not args.mock:
        start_locator_thread(args)
    else:
        insert_mock_data()

    if args.display_pokestops or args.display_lured:
        Pokestop.IGNORE = False

    if args.display_lured:
        Pokestop.LURED_ONLY = True

    if args.display_gyms:
        Gym.IGNORE = False

    #Coordination transformation is needed inside China to display right map.
    if args.china:
        Pokemon.CHINA = True
        Pokestop.CHINA = True
        Gym.CHINA = True

    app = Pogom(__name__)
    config['ROOT_PATH'] = app.root_path
    if args.gmaps_key is not None:
        config['GMAPS_KEY'] = args.gmaps_key
    else:
        config['GMAPS_KEY'] = load_credentials(os.path.dirname(os.path.realpath(__file__)))['gmaps_key']
    app.run(threaded=True, debug=args.debug, host=args.host, port=args.port)
