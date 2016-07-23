#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import argparse
import json
import logging
import os
import random
import re
import struct
import sys
import threading
import time

from google.protobuf.internal import encoder
from google.protobuf.message import DecodeError
from gpsoauth import perform_master_login, perform_oauth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import ConnectionError
from requests.models import InvalidURL
from s2sphere import *
from transform import *
import requests

import config
import db
import pokemon_pb2
import utils


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = (
    'https://sso.pokemon.com/sso/login?service='
    'https://sso.pokemon.com/sso/oauth2.0/callbackAuthorize'
)
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
APP = 'com.nianticlabs.pokemongo'

with open('credentials.json') as file:
    credentials = json.load(file)

PTC_CLIENT_SECRET = credentials.get('ptc_client_secret', None)
ANDROID_ID = credentials.get('android_id', None)
SERVICE = credentials.get('service', None)
CLIENT_SIG = credentials.get('client_sig', None)
GOOGLEMAPS_KEY = credentials.get('gmaps_key', None)

# TODO: these should go away
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0
NEXT_LAT = 0
NEXT_LONG = 0
# /TODO

pokemons = {}
workers = {}
local_data = threading.local()


class CannotGetProfile(Exception):
    """As name says, raised when login service is unreachable

    This should make thread sleep for a moment and restart itself.
    """


def configure_logger(filename='worker.log'):
    logging.basicConfig(
        filename=filename,
        format=(
            '[%(asctime)s][%(threadName)10s][%(levelname)8s][L%(lineno)4d] '
            '%(message)s'
        ),
        style='{',
        level=logging.INFO,
    )

logger = logging.getLogger()


def debug(message):
    logger.info(message)


def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)


def get_neighbours():
    origin = CellId.from_lat_lng(
        LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)
    ).parent(15)
    walk = [origin.id()]

    # 10 before and 10 after

    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk


def f2i(float):
    return struct.unpack('<Q', struct.pack('<d', float))[0]


def f2h(float):
    return hex(struct.unpack('<Q', struct.pack('<d', float))[0])


def h2f(hex):
    return struct.unpack('<d', struct.pack('<Q', int(hex, 16)))[0]


def set_location_coords(lat, long, alt):
    global COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE
    global FLOAT_LAT, FLOAT_LONG
    FLOAT_LAT = lat
    FLOAT_LONG = long
    COORDS_LATITUDE = f2i(lat)  # 0x4042bd7c00000000 # f2i(lat)
    COORDS_LONGITUDE = f2i(long)  # 0xc05e8aae40000000 #f2i(long)
    COORDS_ALTITUDE = f2i(alt)


def get_location_coords():
    return (COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)


def retrying_api_req(service, api_endpoint, access_token, *args, **kwargs):
    while True:
        try:
            response = api_req(
                service,
                api_endpoint,
                access_token,
                *args,
                **kwargs
            )
            if response:
                return response
            logger.debug('retrying_api_req: api_req returned None, retrying')
        except (InvalidURL, ConnectionError, DecodeError) as e:
            logger.debug(
                'retrying_api_req: request error (%s), retrying',
                str(e)
            )
        time.sleep(1)


def api_req(service, api_endpoint, access_token, *args, **kwargs):
    p_req = pokemon_pb2.RequestEnvelop()
    p_req.rpc_id = 1469378659230941192

    p_req.unknown1 = 2

    (p_req.latitude, p_req.longitude, p_req.altitude) = \
        get_location_coords()

    p_req.unknown12 = 989

    if 'useauth' not in kwargs or not kwargs['useauth']:
        p_req.auth.provider = service
        p_req.auth.token.contents = access_token
        p_req.auth.token.unknown13 = 14
    else:
        p_req.unknown11.unknown71 = kwargs['useauth'].unknown71
        p_req.unknown11.unknown72 = kwargs['useauth'].unknown72
        p_req.unknown11.unknown73 = kwargs['useauth'].unknown73

    for arg in args:
        p_req.MergeFrom(arg)

    protobuf = p_req.SerializeToString()

    session = local_data.api_session
    r = session.post(api_endpoint, data=protobuf, verify=False)

    p_ret = pokemon_pb2.ResponseEnvelop()
    p_ret.ParseFromString(r.content)

    if False:  # VERBOSE_DEBUG
        print 'REQUEST:'
        print p_req
        print 'Response:'
        print p_ret
        print '\n\n'
    time.sleep(0.51)
    return p_ret


def get_api_endpoint(service, access_token, api=API_URL):
    profile_response = None
    while not profile_response:
        profile_response = retrying_get_profile(
            service,
            access_token,
            api,
            None
        )
        if not hasattr(profile_response, 'api_url'):
            logger.debug('get_profile returned no api_url, retrying')
            profile_response = None
            continue
        if not len(profile_response.api_url):
            logger.debug('get_profile returned no-len api_url, retrying')
            profile_response = None
    return 'https://%s/rpc' % profile_response.api_url


def retrying_get_profile(service, access_token, api, useauth, *reqq):
    profile_response = None
    times_tried = 0
    while not profile_response:
        if times_tried > 5:
            raise CannotGetProfile
        profile_response = get_profile(
            service, access_token, api, useauth, *reqq
        )
        if not getattr(profile_response, 'payload'):
            logger.debug('get_profile returned no or no-len payload, retrying')
            profile_response = None
            times_tried += 1
            continue
    return profile_response


def get_profile(service, access_token, api, useauth, *reqq):
    req = pokemon_pb2.RequestEnvelop()
    req1 = req.requests.add()
    req1.type = 2
    if len(reqq) >= 1:
        req1.MergeFrom(reqq[0])

    req2 = req.requests.add()
    req2.type = 126
    if len(reqq) >= 2:
        req2.MergeFrom(reqq[1])

    req3 = req.requests.add()
    req3.type = 4
    if len(reqq) >= 3:
        req3.MergeFrom(reqq[2])

    req4 = req.requests.add()
    req4.type = 129
    if len(reqq) >= 4:
        req4.MergeFrom(reqq[3])

    req5 = req.requests.add()
    req5.type = 5
    if len(reqq) >= 5:
        req5.MergeFrom(reqq[4])
    return retrying_api_req(service, api, access_token, req, useauth=useauth)


def login_google(username, password):
    logger.info('Google login for: %s', username)
    r1 = perform_master_login(username, password, ANDROID_ID)
    r2 = perform_oauth(
        username,
        r1.get('Token', ''),
        ANDROID_ID,
        SERVICE,
        APP,
        CLIENT_SIG,
    )
    return r2.get('Auth')


def login_ptc(username, password):
    logger.info('PTC login for: %s', username)
    head = {'User-Agent': 'Niantic App'}
    session = local_data.api_session
    r = session.get(LOGIN_URL, headers=head)
    try:
        jdata = json.loads(r.content)
    except ValueError:
        logger.warning('login_ptc: could not decode JSON from %s', r.content)
        return None
    # Maximum password length is 15
    # (sign in page enforces this limit, API does not)
    if len(password) > 15:
        logger.debug('Trimming password to 15 characters')
        password = password[:15]

    data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': password,
    }
    r1 = session.post(LOGIN_URL, data=data, headers=head)

    ticket = None
    try:
        ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
    except Exception:
        logger.debug('Error: %s', r1.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': PTC_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = session.post(LOGIN_OAUTH, data=data1)
    access_token = re.sub('&expires.*', '', r2.content)
    access_token = re.sub('.*access_token=', '', access_token)
    return access_token


def get_heartbeat(service, api_endpoint, access_token, response):
    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = '05daf51635c82611d1aac95c0b051d3ec088a930'
    m5.message = m.SerializeToString()
    walk = sorted(get_neighbours())
    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = (
        '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'
        '\000\000\000\000'
    )
    m.lat = COORDS_LATITUDE
    m.long = COORDS_LONGITUDE
    m1.message = m.SerializeToString()
    response = get_profile(
        service,
        access_token,
        api_endpoint,
        response.unknown7,
        m1,
        pokemon_pb2.RequestEnvelop.Requests(),
        m4,
        pokemon_pb2.RequestEnvelop.Requests(),
        m5,
    )

    try:
        payload = response.payload[0]
    except (AttributeError, IndexError):
        return

    heartbeat = pokemon_pb2.ResponseEnvelop.HeartbeatPayload()
    heartbeat.ParseFromString(payload)
    return heartbeat


def get_token(service, username, password):
    if service == 'ptc':
        global_token = None
        while not global_token:
            global_token = login_ptc(username, password)
            if not global_token:
                logger.info('Could not login to PTC - sleeping')
                time.sleep(random.randint(10, 20))
    else:
        global_token = login_google(username, password)
    return global_token


def login(username, password, service):
    access_token = get_token(service, username, password)
    if access_token is None:
        raise Exception('[-] Wrong username/password')

    logger.debug('RPC Session Token: %s...', access_token[:25])

    api_endpoint = get_api_endpoint(service, access_token)
    if api_endpoint is None:
        raise Exception('[-] RPC server offline')

    logger.debug('Received API endpoint: %s', api_endpoint)

    profile_response = retrying_get_profile(
        service,
        access_token,
        api_endpoint,
        None,
    )
    if profile_response is None or not profile_response.payload:
        raise Exception('Could not get profile')

    logger.info('Login successful')

    payload = profile_response.payload[0]
    profile = pokemon_pb2.ResponseEnvelop.ProfilePayload()
    profile.ParseFromString(payload)
    logger.debug('Username: %s', profile.profile.username)

    creation_time = datetime.fromtimestamp(
        int(profile.profile.creation_time) / 1000
    )
    logger.debug(
        'You started playing Pokemon Go on: %s',
        creation_time.strftime('%Y-%m-%d %H:%M:%S')
    )

    for curr in profile.profile.currency:
        logger.debug('%s: %s', curr.type, curr.amount)

    return api_endpoint, access_token, profile_response


class Slave(threading.Thread):
    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        worker_no=None,
        points=None,
    ):
        super(Slave, self).__init__(group, target, name)
        self.worker_no = worker_no
        local_data.worker_no = worker_no
        self.points = points
        self.count_points = len(self.points)
        self.step = 0
        self.cycle = 0
        self.seen = 0

    def run(self):
        self.cycle = 1
        self.error_code = None

        # Login sequentially for PTC
        service = config.ACCOUNTS[self.worker_no][2]
        api_session = local_data.api_session = requests.session()
        api_session.headers.update({'User-Agent': 'Niantic App'})
        api_session.verify = False

        try:
            api_endpoint, access_token, profile_response = login(
                username=config.ACCOUNTS[self.worker_no][0],
                password=config.ACCOUNTS[self.worker_no][1],
                service=service,
            )
        except CannotGetProfile:
            # OMG! Sleep for a bit and restart the thread
            self.error_code = 'LOGIN FAIL'
            time.sleep(random.randint(5, 10))
            start_worker(self.worker_no, self.points)
            return
        while self.cycle < 2:
            self.main(service, api_endpoint, access_token, profile_response)
            self.cycle += 1
            if self.cycle < 2:
                self.error_code = 'SLEEP'
                time.sleep(random.randint(30, 60))
                self.error_code = None
        self.error_code = 'RESTART'
        time.sleep(random.randint(30, 60))
        start_worker(self.worker_no, self.points)

    def main(self, service, api_endpoint, access_token, profile_response):
        session = db.Session()
        self.seen = 0
        for i, point in enumerate(self.points):
            logger.info('Visiting point %d (%s %s)', i, point[0], point[1])
            add_to_db = []
            process_step(
                service,
                api_endpoint,
                access_token,
                profile_response,
                add_to_db=add_to_db,
                lat=point[0],
                lon=point[1],
            )
            for spawn_id in add_to_db:
                pokemon = pokemons[spawn_id]
                db.add_sighting(session, spawn_id, pokemon)
                self.seen += 1
            logger.info('Point processed, %d Pokemons seen!', len(add_to_db))
            session.commit()
            # Clear error code and let know that there are Pokemon
            if self.error_code and self.seen:
                self.error_code = None
            self.step += 1
        session.close()
        if self.seen == 0:
            self.error_code = 'NO POKEMON'

    @property
    def status(self):
        if self.error_code:
            msg = self.error_code
        else:
            msg = 'C{cycle},P{seen},{progress:.0f}%'.format(
                cycle=self.cycle,
                seen=self.seen,
                progress=(self.step / float(self.count_points) * 100)
            )
        return '[W{worker_no}: {msg}]'.format(
            worker_no=self.worker_no,
            msg=msg
        )


def process_step(
    service, api_endpoint, access_token, profile_response, add_to_db, lat, lon
):
    logger.debug('Searching for Pokemon at location %s %s', lat, lon)
    step_lat = lat
    step_long = lon
    parent = CellId.from_lat_lng(
        LatLng.from_degrees(lat, lon)
    ).parent(15)
    h = get_heartbeat(
        service,
        api_endpoint,
        access_token,
        profile_response
    )
    hs = [h]
    seen = set([])

    for child in parent.children():
        latlng = LatLng.from_point(Cell(child).get_center())
        set_location_coords(latlng.lat().degrees, latlng.lng().degrees, 0)
        hs.append(get_heartbeat(
            service,
            api_endpoint,
            access_token,
            profile_response
        ))
    set_location_coords(step_lat, step_long, 0)
    visible = []

    for hh in hs:
        try:
            for cell in hh.cells:
                for wild in cell.WildPokemon:
                    hash = wild.SpawnPointId + ':' \
                        + str(wild.pokemon.PokemonId)
                    if hash not in seen:
                        visible.append(wild)
                        seen.add(hash)
        except AttributeError:
            break

    for poke in visible:
        disappear_timestamp = time.time() + poke.TimeTillHiddenMs / 1000
        pokemons[poke.SpawnPointId] = {
            'lat': poke.Latitude,
            'lng': poke.Longitude,
            'disappear_time': disappear_timestamp,
            'id': poke.pokemon.PokemonId,
        }
        add_to_db.append(poke.SpawnPointId)


def get_status_message(workers, count, start_time):
    messages = [workers[i].status.ljust(20) for i in range(count)]
    running_for = datetime.now() - start_time
    random_worker = workers[0]  # all should have the same params
    output = [
        'PokeMiner\trunning for {}'.format(running_for),
        '{} workers, each visiting {} points per cycle'.format(
            len(workers), random_worker.count_points
        ),
        '',
    ]
    previous = 0
    for i in range(4, count + 4, 4):
        output.append('\t'.join(messages[previous:i]))
        previous = i
    return '\n'.join(output)


def start_worker(worker_no, points):
    # Ok I NEED to global this here
    global workers
    logger.info('Worker (re)starting up!')
    worker = Slave(
        name='worker-%d' % worker_no,
        worker_no=worker_no,
        points=points
    )
    worker.daemon = True
    worker.start()
    workers[worker_no] = worker


def spawn_workers(workers, status_bar=True):
    points = utils.get_points_per_worker()
    start_time = datetime.now()
    count = config.GRID[0] * config.GRID[1]
    for worker_no in range(count):
        start_worker(worker_no, points[worker_no])
    while True:
        if status_bar:
            if sys.platform == 'win32':
                _ = os.system('cls')
            else:
                _ = os.system('clear')
            print get_status_message(workers, count, start_time)
        time.sleep(0.5)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--no-status-bar',
        dest='status_bar',
        help='Log to console instead of displaying status bar',
        action='store_false',
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=logging.INFO
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.log_level)
    if args.status_bar:
        configure_logger(filename='worker.log')
        logger.info('-' * 30)
        logger.info('Starting up!')
    else:
        configure_logger(filename=None)
    spawn_workers(workers, status_bar=args.status_bar)
