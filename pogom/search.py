#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import struct
import logging
from threading import Thread
import requests
import time

from pgoapi import PGoApi
from pgoapi.utilities import f2i, h2f, get_cellid, encode, get_pos_by_name

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
REQ_SLEEP = 1
api = PGoApi()


class Search(Thread):
    def __init__(self, args, queue):
        super(Search, self).__init__()
        self.queue = queue
        self.args = args
        self.name = 'search_thread'
        self.encoder = json.JSONEncoder()

    def run(self):
        while True:
            self.search(self.args)
            log.info("Scanning complete")

    def send_map_request(self, api, position):
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

    @staticmethod
    def generate_location_steps(initial_location, num_steps):
        pos, x, y, dx, dy = 1, 0, 0, 0, -1

        while -num_steps / 2 < x <= num_steps / 2 and -num_steps / 2 < y <= num_steps / 2:
            yield (x * 0.0025 + initial_location[0], y * 0.0025 + initial_location[1], 0)

            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx

            x, y = x + dx, y + dy

    def login(self, args, position):
        log.info('Attempting login.')

        api.set_position(*position)

        while not api.login(args.auth_service, args.username, args.password):
            log.info('Login failed. Trying again.')
            time.sleep(REQ_SLEEP)

        log.info('Login successful.')

    def search(self, args):
        num_steps = args.step_limit
        position = (config['ORIGINAL_LATITUDE'], config['ORIGINAL_LONGITUDE'], 0)

        if api._auth_provider and api._auth_provider._ticket_expire:
            remaining_time = api._auth_provider._ticket_expire / 1000 - time.time()

            if remaining_time > 60:
                log.info("Skipping login process since already logged in for another {:.2f} seconds".format(
                    remaining_time))
            else:
                self.login(args, position)
        else:
            self.login(args, position)

        i = 1
        for step_location in self.generate_location_steps(position, num_steps):
            log.info('Scanning step {:d} of {:d}.'.format(i, num_steps ** 2))
            log.debug('Scan location is {:f}, {:f}'.format(step_location[0], step_location[1]))

            response_dict = self.send_map_request(api, step_location)

            self.queue.put(step_location)

            while not response_dict:
                log.info('Map Download failed. Trying again.')
                response_dict = self.send_map_request(api, step_location)
                time.sleep(REQ_SLEEP)

            try:
                parse_map(response_dict)
            except KeyError:
                log.error('Scan step failed. Response dictionary key error.')

            log.info('Completed {:5.2f}% of scan.'.format(float(i) / num_steps ** 2 * 100))
            i += 1
            time.sleep(REQ_SLEEP)
