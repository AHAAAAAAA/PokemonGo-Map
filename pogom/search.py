#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Search Architecture:
 - Have a list of accounts
 - Create an "overseer" thread
 - Search Overseer:
   - Tracks incoming new location values
   - Tracks "paused state"
   - During pause or new location will clears current search queue
   - Starts search_worker threads
 - Search Worker Threads each:
   - Have a unique API login
   - Listens to the same Queue for areas to scan
   - Can re-login as needed
   - Shares a global lock for map parsing
'''

import logging
import time
import math
import threading

from threading import Thread, Lock
from queue import Queue, Empty

from pgoapi import PGoApi
from pgoapi.utilities import f2i, get_cellid

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'

def get_new_coords(init_loc, distance, bearing):
    """ Given an initial lat/lng, a distance(in kms), and a bearing (degrees),
    this will calculate the resulting lat/lng coordinates.
    """
    R = 6378.1 #km radius of the earth
    bearing = math.radians(bearing)

    init_coords = [math.radians(init_loc[0]), math.radians(init_loc[1])] # convert lat/lng to radians

    new_lat = math.asin( math.sin(init_coords[0])*math.cos(distance/R) +
        math.cos(init_coords[0])*math.sin(distance/R)*math.cos(bearing))

    new_lon = init_coords[1] + math.atan2(math.sin(bearing)*math.sin(distance/R)*math.cos(init_coords[0]),
        math.cos(distance/R)-math.sin(init_coords[0])*math.sin(new_lat))

    return [math.degrees(new_lat), math.degrees(new_lon)]

def generate_location_steps(initial_loc, step_count):
    #Bearing (degrees)
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    pulse_radius = 0.07                 # km - radius of players heartbeat is 70m
    xdist = math.sqrt(3)*pulse_radius   # dist between column centers
    ydist = 3*(pulse_radius/2)          # dist between row centers

    yield (initial_loc[0], initial_loc[1], 0) #insert initial location

    ring = 1
    loc = initial_loc
    while ring < step_count:
        #Set loc to start at top left
        loc = get_new_coords(loc, ydist, NORTH)
        loc = get_new_coords(loc, xdist/2, WEST)
        for direction in range(6):
            for i in range(ring):
                if direction == 0: # RIGHT
                    loc = get_new_coords(loc, xdist, EAST)
                if direction == 1: # DOWN + RIGHT
                    loc = get_new_coords(loc, ydist, SOUTH)
                    loc = get_new_coords(loc, xdist/2, EAST)
                if direction == 2: # DOWN + LEFT
                    loc = get_new_coords(loc, ydist, SOUTH)
                    loc = get_new_coords(loc, xdist/2, WEST)
                if direction == 3: # LEFT
                    loc = get_new_coords(loc, xdist, WEST)
                if direction == 4: # UP + LEFT
                    loc = get_new_coords(loc, ydist, NORTH)
                    loc = get_new_coords(loc, xdist/2, WEST)
                if direction == 5: # UP + RIGHT
                    loc = get_new_coords(loc, ydist, NORTH)
                    loc = get_new_coords(loc, xdist/2, EAST)
                yield (loc[0], loc[1], 0)
        ring += 1


#
# A fake search loop which does....nothing!
#
def fake_search_loop():
    while True:
        log.info('Fake search loop running')
        time.sleep(10)


# The main search loop that keeps an eye on the over all process
def search_overseer_thread(args, new_location_queue, pause_bit):

    log.info('Search overseer starting')

    search_items_queue = Queue()
    parse_lock = Lock()

    # Create a search_worker_thread per account
    log.info('Starting search worker threads')
    for i, account in enumerate(args.accounts):
        log.debug('Starting search worker thread %d for user %s', i, account['username'])
        t = Thread(target=search_worker_thread,
                   name='search_worker_{}'.format(i),
                   args=(args, account, search_items_queue, parse_lock))
        t.daemon = True
        t.start()

    # A place to track the current location
    current_location = False;

    # The real work starts here but will halt on pause_bit.set()
    while True:

        # paused; clear queue if needed, otherwise sleep and loop
        if pause_bit.is_set():
            if not search_items_queue.empty():
                try:
                    while True:
                        search_items_queue.get_nowait()
                except Empty:
                    pass
            time.sleep(1)
            continue

        # If a new location has been passed to us, get the most recent one
        if not new_location_queue.empty():
            log.info('New location caught, moving search grid')
            try:
                while True:
                    current_location = new_location_queue.get_nowait()
            except Empty:
                pass

            # We (may) need to clear the search_items_queue
            if not search_items_queue.empty():
                try:
                    while True:
                        search_items_queue.get_nowait()
                except Empty:
                    pass

        # If there are no search_items_queue either the loop has finished (or been
        # cleared above) -- either way, time to fill it back up
        if search_items_queue.empty():
            log.debug('Search queue empty, restarting loop')
            for step, step_location in enumerate(generate_location_steps(current_location, args.step_limit), 1):
                log.debug('Queueing step %d @ %f/%f/%f', step, step_location[0], step_location[1], step_location[2])
                search_args = (step, step_location)
                search_items_queue.put(search_args)
        # else:
        #     log.info('Search queue processing, %d items left', search_items_queue.qsize())

        # Now we just give a little pause here
        time.sleep(1)


def search_worker_thread(args, account, search_items_queue, parse_lock):

    log.debug('Search worker thread starting')

    # Create the API instance this will use
    api = PGoApi()

    # The forever loop for the thread
    while True:

        # Grab the next thing to search (when available)
        step, step_location = search_items_queue.get()

        log.info('Searching step %d, remaining %d', step, search_items_queue.qsize())

        # The loop to try very hard to scan this step
        failed_consecutive = 0
        while True:

            # If requests have been too many, sleep longer
            if failed_consecutive >= config['REQ_MAX_FAILED']:
                log.error('Servers under heavy load, waiting for extended (%g) sleep', config['REQ_MAX_FAILED'])
                time.sleep(config['REQ_HEAVY_SLEEP'])
                failed_consecutive = 0

            # Ok, let's get started -- check our login status
            check_login(args, account, api)

            # Make the actual request (finally!)
            response_dict = map_request(api, step_location)

            # G'damnit, nothing back. Mark it up, sleep, carry on
            if not response_dict:
                log.error('Search area download failed, sleeping for %g and trying again', args.scan_delay)
                failed_consecutive += 1
                time.sleep(args.scan_delay)
                continue

            # Got the response, lock for parsing and do so (or fail, whatever)
            with parse_lock:
                try:
                    parsed = parse_map(response_dict, step_location)
                    log.debug('Scan step %s completed', step)
                    break # All done, get out of the request-retry loop
                except KeyError:
                    log.error('Parsing map response failed, retyring request')
                    failed_consecutive += 1

        time.sleep(args.scan_delay)
        search_items_queue.task_done()


def check_login(args, account, api):

    # Logged in? Enough time left? Cool!
    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire/1000 - time.time()
        if remaining_time > 60:
            log.debug('Credentials remain valid for another %f seconds', remaining_time)
            return

    # Ohhh, not good-to-go, getter' fixed up
    while not api.login(account['auth_service'], account['username'], account['password']):
        log.error('Failed to login to Pokemon Go. Trying again in %g seconds', args.login_delay)
        time.sleep(args.login_delay)

    log.debug('Login for account %s successful', account['username'])


def map_request(api, position):
    try:
        api.set_position(*position)
        api.get_map_objects(latitude=f2i(position[0]),
                            longitude=f2i(position[1]),
                            since_timestamp_ms=TIMESTAMP,
                            cell_id=get_cellid(position[0], position[1]))
        return api.call()
    except Exception as e:
        log.warning('Exception while downloading map: %s', e)
        return False