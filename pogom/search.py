#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Search Architecture:
 - Create a Queue
   - Holds a list of locations to scan
 - Create N search threads
   - Each search thread will be responsible for hitting the API for a given scan location
 - Create a "overseer" loop
   - Creates/updates the search grid, populates the Queue, and waits for the current search itteration to complete
   -
'''

import logging
import time
import math
import threading

from threading import Thread, Lock
from queue import Queue

from pgoapi import PGoApi
from pgoapi.utilities import f2i, get_cellid

from pogom.utils import get_location_key

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
api = PGoApi()

search_dict = {}
search_queue = Queue()


def calculate_lng_degrees(lat):
    return float(lng_gap_meters) / \
        (meters_per_degree * math.cos(math.radians(lat)))


def send_map_request(api, position):
    try:
        api_copy = api.copy()
        api_copy.set_position(*position)
        api_copy.get_map_objects(latitude=f2i(position[0]),
                                 longitude=f2i(position[1]),
                                 since_timestamp_ms=TIMESTAMP,
                                 cell_id=get_cellid(position[0], position[1]))
        return api_copy.call()
    except Exception as e:
        log.warning("Uncaught exception when downloading map " + str(e))
        return False

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

    pulse_radius = 0.1                  # km - radius of players heartbeat is 100m
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


def login(args, position):
    log.info('Attempting login to Pokemon Go.')

    api.set_position(*position)

    while not api.login(args.auth_service, args.username, args.password):
        log.info('Failed to login to Pokemon Go. Trying again in {:g} seconds.'.format(args.login_delay))
        time.sleep(args.login_delay)

    log.info('Login to Pokemon Go successful.')


#
# Search Threads Logic
#
def create_search_threads(num):
    search_threads = []
    for i in range(num):
        t = Thread(target=search_thread, name='search_thread-{}'.format(i), args=(search_queue,))
        t.daemon = True
        t.start()
        search_threads.append(t)


def search_thread(q):
    threadname = threading.currentThread().getName()
    log.debug("Search thread {}: started and waiting".format(threadname))
    while True:
        search_args = q.get()
        if not search_args['skip']:
            log.debug("{}: processing itteration {} step {}".format(threadname, search_args['iteration'], search_args['step']))
            response_dict = {}
            failed_consecutive = 0
            while not response_dict:
                response_dict = send_map_request(api, search_args['step_location'])
                if response_dict:
                    with search_args['lock']:
                        try:
                            parse_map(response_dict, search_args['iteration'], search_args['step'], search_args['step_location'])
                            log.debug("{}: itteration {} step {} complete".format(threadname, search_args['iteration'], search_args['step']))
                        except KeyError:
                            log.error('Search thread failed. Response dictionary key error')
                            log.debug('{}: itteration {} step {} failed. Response dictionary\
                                key error.'.format(threadname, search_args['iteration'], search_args['step']))
                            failed_consecutive += 1
                            if(failed_consecutive >= config['REQ_MAX_FAILED']):
                                log.error('Niantic servers under heavy load. Waiting before trying again')
                                time.sleep(config['REQ_HEAVY_SLEEP'])
                                failed_consecutive = 0
                            response_dict = {}
                else:
                    log.info('Map download failed, waiting and retrying')
                    log.debug('{}: itteration {} step {} failed'.format(threadname, search_args['iteration'], search_args['step']))
                    time.sleep(config['REQ_SLEEP'])

            time.sleep(config['REQ_SLEEP'])
        q.task_done()


#
# Search Overseer
#
def search_loop(args):
    i = 0
    while True:
        log.info("Search loop {} starting".format(i))
        try:
            search(args, i)
            log.info("Search loop {} complete.".format(i))
            i += 1
        except Exception as e:
            log.error('Scanning error @ {0.__class__.__name__}: {0}'.format(e))
        finally:
            if args.thread_delay > 0:
                log.info('Waiting {:g} seconds before beginning new scan.'.format(args.thread_delay))
                time.sleep(args.thread_delay)


#
# Overseer main logic
#
def search(args, i):
    num_steps = args.step_limit

    position = (config['SEARCH_LOCATIONS'][0]['lat'], config['SEARCH_LOCATIONS'][0]['lon'], 0)

    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire/1000 - time.time()

        if remaining_time > 60:
            log.info("Skipping Pokemon Go login process since already logged in \
                for another {:.2f} seconds".format(remaining_time))
        else:
            login(args, position)
    else:
        login(args, position)

    lock = Lock()

    search_locations = []
    for loc in config['SEARCH_LOCATIONS']:
        search_key = get_location_key(loc['lat'], loc['lon'])
        search_dict[search_key] = []
        search_locations.append(
            list((search_key, step, step_location) for step, step_location in enumerate(
                generate_location_steps((loc['lat'], loc['lon'], 0), num_steps), 1)))

    for step_locations in zip(*search_locations):
        for search_key, step, step_location in step_locations:
            log.debug("Queue search itteration {}, step {}".format(i, step))
            search_args = { 'iteration': i, 'step_location': step_location, 'step': step, 'lock': lock, 'skip': False }
            search_queue.put(search_args)
            search_dict[search_key].append(search_args)

    # Wait until this scan itteration queue is empty (not nessearily done)
    while not search_queue.empty():
        log.debug("Waiting for current search queue to complete (remaining: {})".format(search_queue.qsize()))
        time.sleep(1)

    # Don't let this method exit until the last item has ACTUALLY finished
    search_queue.join()

#
# A fake search loop which does....nothing!
#
def fake_search_loop():
    while True:
        log.info('Fake search loop running...')
        time.sleep(10)

#
# Skips the searches queued for a particular location
#
def stop_search(lat, lon):
    search_key = get_location_key(lat, lon)
    if search_key in search_dict:
        for search_args in search_dict[search_key]:
            search_args['skip'] = True