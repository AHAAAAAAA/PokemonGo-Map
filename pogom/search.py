#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import logging
import time
import threading
import Queue
import itertools

from pgoapi import PGoApi
from pgoapi.utilities import f2i, get_cellid

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = ('\000\000\000\000\000\000\000\000\000\000\000'
             '\000\000\000\000\000\000\000\000\000\000')
REQ_SLEEP = 1
api = PGoApi()


def send_map_request(api, position):
    try:
        api.set_position(*position)
        api.get_map_objects(latitude=f2i(position[0]),
                            longitude=f2i(position[1]),
                            since_timestamp_ms=TIMESTAMP,
                            cell_id=get_cellid(position[0], position[1]))
        return api.call()
    except Exception as e:
        log.warn("Uncaught exception when downloading map " + e)
        return False


def generate_location_steps(initial_location, num_steps):
    coord_len = num_steps // 2
    coords = [i for i in range(-coord_len, coord_len + 1)]

    for x, y in itertools.product(coords, repeat=2):
        yield (x * 0.0025 + initial_location[0],
               y * 0.0025 + initial_location[1],
               0)


def login(args, position):
    log.info('Attempting login.')

    api.set_position(*position)

    while not api.login(args.auth_service, args.username, args.password):
        log.info('Login failed. Trying again.')
        time.sleep(REQ_SLEEP)

    log.info('Login successful.')


class Search(threading.Thread):
    def __init__(self, args, queue=Queue.LifoQueue(), *posargs, **kwargs):
        super().__init__(*posargs, **kwargs)
        self._stop = threading.Event()
        self.args = args
        self.queue = queue

    def search(self):
        num_steps = self.args.step_limit
        position = (config['ORIGINAL_LATITUDE'],
                    config['ORIGINAL_LONGITUDE'],
                    0)

        provider = api._auth_provider

        if provider:
            expire_time = api._auth_provider._ticket_expire
            remaining_time = expire_time / 1000 - time.time()

            if remaining_time > 60:
                log.info("Skipping login process since already logged in for"
                         " another {:.2f} seconds".format(
                             remaining_time))
            else:
                login(self.args, position)
        else:
            login(self.args, position)

        i = 1
        for step_location in generate_location_steps(position, num_steps):
            log.info('Scanning step {:d} of {:d}.'.format(i, num_steps**2))
            log.debug('Scan location is {:f}, {:f}'.format(
                step_location[0], step_location[1]))

            self.queue.put(step_location)

            response_dict = send_map_request(api, step_location)
            while not response_dict:
                log.info('Map Download failed. Trying again.')
                response_dict = send_map_request(api, step_location)
                time.sleep(REQ_SLEEP)

            try:
                parse_map(response_dict)
            except KeyError:
                log.error('Scan step failed. Response dictionary key error.')

            log.info('Completed {:5.2f}% of scan.'.format(
                float(i) / num_steps**2 * 100))
            i += 1
            time.sleep(REQ_SLEEP)

    def run(self):
        while not self._stop.is_set():
            self.search()
            log.info("Scanning complete.")
            time.sleep(1)
