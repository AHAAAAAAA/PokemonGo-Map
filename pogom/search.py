#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import struct
import logging
import requests
import math
import time

from pgoapi import PGoApi
from pgoapi.utilities import f2i, h2f, get_cellid, encode, get_pos_by_name

from . import config
from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
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
        log.warn("Uncaught exception when downloading map "+ e)
        return False

def hex_transform(x,y,r,il):
    return (x+y/2)*r[0]+il[0],(0.886*y)*r[1]+il[1],0

def generate_location_steps(il, num_steps):
    pos, x, y, dx, dy, m = 1, 0., 0., 0, -1, 280
    conv = float(111111)                            # ~meters per degree
    r = m/conv, m/conv / math.cos(il[0]*0.0174533)  # Conversion of radius from meters to deg
    yield hex_transform(x,y,r,il)
    for n in range(1,num_steps):
        n+=1
        for i in range(1, n):
            x+=1
            yield hex_transform(x,y,r,il)
        for i in range(1, n-1):
            y+=1
            yield hex_transform(x,y,r,il)
        for i in range(1, n):
            x-=1
            y+=1
            yield hex_transform(x,y,r,il)
        for i in range(1, n):
            x-=1
            yield hex_transform(x,y,r,il)
        for i in range(1, n):
            y-=1
            yield hex_transform(x,y,r,il)
        for i in range(1, n):
            x+=1
            y-=1
            yield hex_transform(x,y,r,il)
    for i in range(1, num_steps):
        x+=1
        yield hex_transform(x,y,r,il)

def login(args, position):
    log.info('Attempting login to Pokemon Go.')

    api.set_position(*position)

    while not api.login(args.auth_service, args.username, args.password):
        log.info('Failed to login to Pokemon Go. Trying again.')
        time.sleep(REQ_SLEEP)

    log.info('Login to Pokemon Go successful.')


def search(args):
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

    i = 1

    for step_location in generate_location_steps(position, num_steps):
        log.info('Scanning step {:d} of {:d}.'.format(i, 3*num_steps**2-3*num_steps+1))
        log.debug('Scan location is {:f}, {:f}'.format(step_location[0], step_location[1]))

        response_dict = send_map_request(api, step_location)
        while not response_dict:
            log.info('Map Download failed. Trying again.')
            response_dict = send_map_request(api, step_location)
            time.sleep(REQ_SLEEP)

        try:
            parse_map(response_dict)
        except KeyError:
            log.error('Scan step failed. Response dictionary key error.')

        log.info('Completed {:5.2f}% of scan.'.format(float(i) / (3*num_steps**2-3*num_steps+1)*100))
        i += 1
        time.sleep(REQ_SLEEP)


def search_loop(args):
    while True:
        search(args)
        log.info("Scanning complete.")
        time.sleep(1)
