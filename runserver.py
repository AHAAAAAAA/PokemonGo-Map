#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from threading import Thread

from pogom import config
from pogom.app import Pogom
from pogom.search import search
from pogom.utils import get_args, insert_mock_data
from pogom.models import create_tables


def start_locator_thread(args):
    search_thread = Thread(target=search, args=(args,))
    search_thread.daemon = True
    search_thread.name = 'search_thread'
    search_thread.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')

    logging.getLogger("peewee").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.INFO)

    # logging.getLogger("requests").setLevel(logging.DEBUG)
    # logging.getLogger("pgoapi").setLevel(logging.DEBUG)
    # logging.getLogger("rpc_api").setLevel(logging.DEBUG)

    args = get_args()
    create_tables()

    if not args.mock:
        start_locator_thread(args)
    else:
        insert_mock_data(args.location, 6)

    app = Pogom(__name__)
    config['ROOT_PATH'] = app.root_path
    app.run(threaded=True, debug=args.debug, host=args.host, port=args.port)
