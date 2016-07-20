#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, load_credentials

from pogom.models import create_tables, Pokemon
from pogom.pgoapi.utilities import get_pos_by_name

log = logging.getLogger(__name__)

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

    if args.ignore:
        Pokemon.IGNORE = [i.lower().strip() for i in args.ignore.split(',')]
    elif args.only:
        Pokemon.ONLY = [i.lower().strip() for i in args.only.split(',')]

    app = Pogom(__name__)
    config['ROOT_PATH'] = app.root_path
    if args.gmaps_key is not None:
        config['GMAPS_KEY'] = args.gmaps_key
    else:
        config['GMAPS_KEY'] = load_credentials(os.path.dirname(os.path.realpath(__file__)))['gmaps_key']

    #lets pass the args over to pogom search
    app.initSearch(args)
    #now start the server
    app.run(threaded=True, debug=args.debug, host=args.host, port=args.port)
