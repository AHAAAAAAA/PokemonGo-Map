#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time

from pgoapi import PGoApi
from pgoapi.utilities import f2i, get_cellid

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
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
        log.warn("Uncaught exception when downloading map " + str(e))
        return False


def generate_location_steps(initial_location, num_steps):
    pos, x, y, dx, dy = 1, 0, 0, 0, -1

    while -num_steps / 2 < x <= num_steps / 2 and -num_steps / 2 < y <= num_steps / 2:
        yield (x * 0.00125 + initial_location[0], y * 0.00175 + initial_location[1], 0)

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            dx, dy = -dy, dx

        x, y = x + dx, y + dy


def login(args, position):
    log.info('Attempting login to Pokemon Go.')

    api.set_position(*position)

    while not api.login(args.auth_service, args.username, args.password):
        log.info('Failed to login to Pokemon Go. Trying again.')
        time.sleep(config['REQ_SLEEP'])

    log.info('Login to Pokemon Go successful.')


def search(args, i):
    num_steps = args.step_limit
    position = (config['ORIGINAL_LATITUDE'], config['ORIGINAL_LONGITUDE'], 0)

    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire/1000 - time.time()

        if remaining_time > 60:
            log.info("Skipping Pokemon Go login process since already logged in for another {:.2f} seconds".format(remaining_time))
        else:
            login(args, position)
    else:
        login(args, position)

    for step, step_location in enumerate(generate_location_steps(position, num_steps), 1):
        if 'NEXT_LOCATION' in config:
            log.info('New location found. Starting new scan.')
            config['ORIGINAL_LATITUDE'] = config['NEXT_LOCATION']['lat']
            config['ORIGINAL_LONGITUDE'] = config['NEXT_LOCATION']['lon']
            config.pop('NEXT_LOCATION', None)
            search(args)
            return

        log.info('Scanning step {:d} of {:d}.'.format(step, num_steps**2))
        log.debug('Scan location is {:f}, {:f}'.format(step_location[0], step_location[1]))

        response_dict = {}
        failed_consecutive = 0
        while not response_dict:
            response_dict = send_map_request(api, step_location)
            if response_dict:
                try:
                    parse_map(response_dict, i)
                except KeyError:
                    log.error('Scan step {:d} failed. Response dictionary key error.'.format(step))
                    failed_consecutive += 1
                    if(failed_consecutive >= config['REQ_MAX_FAILED']):
                        log.error('Niantic servers under heavy load. Waiting before trying again')
                        time.sleep(config['REQ_HEAVY_SLEEP'])
                        failed_consecutive = 0
            else:
                log.info('Map Download failed. Trying again.')

        log.info('Completed {:5.2f}% of scan.'.format(float(step) / num_steps**2*100))
        time.sleep(config['REQ_SLEEP'])


def search_loop(args):
    i = 0
    while True:
        log.info("Map iteration: {}".format(i))
        search(args, i)
        log.info("Scanning complete.")
        if args.scan_delay > 1:
            log.info('Waiting {:d} seconds before beginning new scan.'.format(args.scan_delay))
        i += 1
        time.sleep(args.scan_delay)
