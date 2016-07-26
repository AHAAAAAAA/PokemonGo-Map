#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import math

from threading import Thread, Lock
from queue import Queue

from pgoapi import PGoApi
from pgoapi.utilities import f2i, get_cellid

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
api = PGoApi()

#Constants for Hex Grid
#Gap between vertical and horzonal "rows"
lat_gap_meters = 150
lng_gap_meters = 86.6

#111111m is approx 1 degree Lat, which is close enough for this
meters_per_degree = 111111
lat_gap_degrees = float(lat_gap_meters) / meters_per_degree

search_queue = Queue(config['SEARCH_QUEUE_DEPTH'])

def calculate_lng_degrees(lat):
    return float(lng_gap_meters) / (meters_per_degree * math.cos(math.radians(lat)))


def send_map_request(api, position):
    try:
        api.set_position(*position)
        api.get_map_objects(latitude=f2i(position[0]),
                            longitude=f2i(position[1]),
                            since_timestamp_ms=TIMESTAMP,
                            cell_id=get_cellid(position[0], position[1]))
        return api.call()
    except Exception as e:
        log.warning("Uncaught exception when downloading map " + str(e))
        return False


def generate_location_steps(initial_location, num_steps):

    ring = 1 #Which ring are we on, 0 = center
    lat_location = initial_location[0]
    lng_location = initial_location[1]

    yield (initial_location[0],initial_location[1], 0) #Middle circle

    while ring < num_steps:
        #Move the location diagonally to top left spot, then start the circle which will end up back here for the next ring
        #Move Lat north first
        lat_location += lat_gap_degrees
        lng_location -= calculate_lng_degrees(lat_location)

        for direction in range(6):
            for i in range(ring):
                if direction == 0: #Right
                    lng_location += calculate_lng_degrees(lat_location) * 2

                if direction == 1: #Right Down
                    lat_location -= lat_gap_degrees
                    lng_location += calculate_lng_degrees(lat_location)

                if direction == 2: #Left Down
                    lat_location -= lat_gap_degrees
                    lng_location -= calculate_lng_degrees(lat_location)

                if direction == 3: #Left
                    lng_location -= calculate_lng_degrees(lat_location) * 2

                if direction == 4: #Left Up
                    lat_location += lat_gap_degrees
                    lng_location -= calculate_lng_degrees(lat_location)

                if direction == 5: #Right Up
                    lat_location += lat_gap_degrees
                    lng_location += calculate_lng_degrees(lat_location)

                yield (lat_location, lng_location, 0) #Middle circle

        ring += 1


def login(args, position):
    log.info('Attempting login to Pokemon Go.')

    api.set_position(*position)

    while not api.login(args.auth_service, args.username, args.password):
        log.info('Failed to login to Pokemon Go. Trying again.')
        time.sleep(config['REQ_SLEEP'])

    log.info('Login to Pokemon Go successful.')

def create_search_threads(num) :
    search_threads = []
    for i in range(num):
        t = Thread(target=search_thread, name='search_thread {}'.format(i), args=( search_queue,))
        t.daemon = True
        t.start()
        search_threads.append(t)

def search_thread(args):
    queue = args
    while True:
        i, total_steps, step_location, step, lock = queue.get()
        log.debug("Search queue depth is: " + str(queue.qsize()))
        response_dict = {}
        failed_consecutive = 0
        while not response_dict:
            response_dict = send_map_request(api, step_location)
            if response_dict:
                with lock:
                    try:
                        parse_map(response_dict, i, step, step_location)
                    except KeyError:
                        log.error('Scan step {:d} failed. Response dictionary key error.'.format(step))
                        failed_consecutive += 1
                        if(failed_consecutive >= config['REQ_MAX_FAILED']):
                            log.error('Niantic servers under heavy load. Waiting before trying again')
                            time.sleep(config['REQ_HEAVY_SLEEP'])
                            failed_consecutive = 0
                        response_dict = {}
            else:
                log.info('Map Download failed. Trying again.')
                time.sleep(config['REQ_SLEEP'])

        time.sleep(config['REQ_SLEEP'])

def process_search_threads(search_threads, curr_steps, total_steps):
    for thread in search_threads:
        thread.start()
    for thread in search_threads:
        curr_steps += 1
        thread.join()
        log.info('Completed {:5.2f}% of scan.'.format(float(curr_steps) / total_steps*100))
    return curr_steps

def search(args, i):
    num_steps = args.step_limit
    total_steps = (3 * (num_steps**2)) - (3 * num_steps) + 1
    position = (config['ORIGINAL_LATITUDE'], config['ORIGINAL_LONGITUDE'], 0)

    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire/1000 - time.time()

        if remaining_time > 60:
            log.info("Skipping Pokemon Go login process since already logged in for another {:.2f} seconds".format(remaining_time))
        else:
            login(args, position)
    else:
        login(args, position)

    lock = Lock()

    search_threads = []
    curr_steps = 0
    max_threads = args.num_threads

    for step, step_location in enumerate(generate_location_steps(position, num_steps), 1):
        if 'NEXT_LOCATION' in config:
            log.info('New location found. Starting new scan.')
            config['ORIGINAL_LATITUDE'] = config['NEXT_LOCATION']['lat']
            config['ORIGINAL_LONGITUDE'] = config['NEXT_LOCATION']['lon']
            config.pop('NEXT_LOCATION', None)
            search_queue.queue.clear()
            search(args, i)
            return

        search_args = ( i, total_steps, step_location, step, lock)
        search_queue.put(search_args)

def search_loop(args):
    i = 0
    try:
        while True:
            log.info("Map iteration: {}".format(i))
            search(args, i)
            log.info("Scanning complete.")
            if args.scan_delay > 1:
                log.info('Waiting {:f} seconds before beginning new scan.'.format(args.scan_delay))
                time.sleep(args.scan_delay)
            i += 1

    # This seems appropriate
    except Exception as e:
        log.info('{0.__class__.__name__}: {0} - waiting {1} sec(s) before restarting'.format(e, args.scan_delay))
        time.sleep(args.scan_delay)
        search_loop(args)
