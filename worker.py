#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import struct
import json
import requests
import argparse
import getpass
import logging
import threading
import werkzeug.serving
import pokemon_pb2
import time
import random
from google.protobuf.internal import encoder
from google.protobuf.message import DecodeError
from s2sphere import *
from datetime import datetime
from gpsoauth import perform_master_login, perform_oauth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import ConnectionError
from requests.models import InvalidURL
from transform import *

import config
import db
import utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = \
    'https://sso.pokemon.com/sso/login?service=https://sso.pokemon.com/sso/oauth2.0/callbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
APP = 'com.nianticlabs.pokemongo'

with open('credentials.json') as file:
    credentials = json.load(file)

PTC_CLIENT_SECRET = credentials.get('ptc_client_secret', None)
ANDROID_ID = credentials.get('android_id', None)
SERVICE = credentials.get('service', None)
CLIENT_SIG = credentials.get('client_sig', None)
GOOGLEMAPS_KEY = credentials.get('gmaps_key', None)

DEBUG = True
VERBOSE_DEBUG = False  # if you want to write raw request/response to the console
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0
NEXT_LAT = 0
NEXT_LONG = 0
auto_refresh = 0
default_step = 0.001
api_endpoint = None
pokemons = {}
add_to_db = []
gyms = {}
pokestops = {}
numbertoteam = {  # At least I'm pretty sure that's it. I could be wrong and then I'd be displaying the wrong owner team of gyms.
    0: 'Gym',
    1: 'Mystic',
    2: 'Valor',
    3: 'Instinct',
}
origin_lat, origin_lon = None, None
is_ampm_clock = False

# stuff for in-background search thread

search_thread = None
workers = {}


def memoize(obj):
    cache = threading.local().cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string


def debug(message):
    if DEBUG:
        print '[-] {}'.format(message)


def time_left(ms):
    s = ms / 1000
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)
    return (h, m, s)


def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)


def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT,
                                                     FLOAT_LONG)).parent(15)
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
            response = api_req(service, api_endpoint, access_token, *args,
                               **kwargs)
            if response:
                return response
            debug('retrying_api_req: api_req returned None, retrying')
        except (InvalidURL, ConnectionError, DecodeError), e:
            debug('retrying_api_req: request error ({}), retrying'.format(
                str(e)))
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

    session = threading.local().session
    r = session.post(api_endpoint, data=protobuf, verify=False)

    p_ret = pokemon_pb2.ResponseEnvelop()
    p_ret.ParseFromString(r.content)

    if VERBOSE_DEBUG:
        print 'REQUEST:'
        print p_req
        print 'Response:'
        print p_ret
        print '''

'''
    time.sleep(0.51)
    return p_ret


def get_api_endpoint(service, access_token, api=API_URL):
    profile_response = None
    while not profile_response:
        profile_response = retrying_get_profile(service, access_token, api,
                                                None)
        if not hasattr(profile_response, 'api_url'):
            debug(
                'retrying_get_profile: get_profile returned no api_url, retrying')
            profile_response = None
            continue
        if not len(profile_response.api_url):
            debug(
                'get_api_endpoint: retrying_get_profile returned no-len api_url, retrying')
            profile_response = None

    return 'https://%s/rpc' % profile_response.api_url


def retrying_get_profile(service, access_token, api, useauth, *reqq):
    profile_response = None
    while not profile_response:
        profile_response = get_profile(service, access_token, api, useauth,
                                       *reqq)
        if not hasattr(profile_response, 'payload'):
            debug(
                'retrying_get_profile: get_profile returned no payload, retrying')
            profile_response = None
            continue
        if not profile_response.payload:
            debug(
                'retrying_get_profile: get_profile returned no-len payload, retrying')
            profile_response = None

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
    print '[!] Google login for: {}'.format(username)
    r1 = perform_master_login(username, password, ANDROID_ID)
    r2 = perform_oauth(username,
                       r1.get('Token', ''),
                       ANDROID_ID,
                       SERVICE,
                       APP,
                       CLIENT_SIG, )
    return r2.get('Auth')


def login_ptc(username, password):
    print '[!] PTC login for: {}'.format(username)
    head = {'User-Agent': 'Niantic App'}
    session = threading.local().session
    r = session.get(LOGIN_URL, headers=head)

    try:
        jdata = json.loads(r.content)
    except ValueError:
        debug('login_ptc: could not decode JSON from {}'.format(r.content))
        return None

    # Maximum password length is 15 (sign in page enforces this limit, API does not)

    if len(password) > 15:
        print '[!] Trimming password to 15 characters'
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
        if DEBUG:
            print r1.json()['errors'][0]
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


def get_heartbeat(service,
                  api_endpoint,
                  access_token,
                  response, ):
    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = '05daf51635c82611d1aac95c0b051d3ec088a930'
    m5.message = m.SerializeToString()
    walk = sorted(getNeighbors())
    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = \
        "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    m.lat = COORDS_LATITUDE
    m.long = COORDS_LONGITUDE
    m1.message = m.SerializeToString()
    response = get_profile(service,
                           access_token,
                           api_endpoint,
                           response.unknown7,
                           m1,
                           pokemon_pb2.RequestEnvelop.Requests(),
                           m4,
                           pokemon_pb2.RequestEnvelop.Requests(),
                           m5, )

    try:
        payload = response.payload[0]
    except (AttributeError, IndexError):
        return

    heartbeat = pokemon_pb2.ResponseEnvelop.HeartbeatPayload()
    heartbeat.ParseFromString(payload)
    return heartbeat


def get_token(service, username, password):
    """
    Get token if it's not None
    :return:
    :rtype:
    """
    if service == 'ptc':
        global_token = None
        while not global_token:
            global_token = login_ptc(username, password)
            if not global_token:
                print('Could not login to PTC - sleeping')
                time.sleep(random.randint(10, 20))
    else:
        global_token = login_google(username, password)
    return global_token


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-st', '--step-limit', help='Steps', required=True)
    parser.add_argument(
        '-d', '--debug', help='Debug Mode', action='store_true')
    parser.set_defaults(DEBUG=True)
    return parser.parse_args()


def login(username, password, service):
    access_token = get_token(service, username, password)
    if access_token is None:
        raise Exception('[-] Wrong username/password')

    print '[+] RPC Session Token: {} ...'.format(access_token[:25])

    api_endpoint = get_api_endpoint(service, access_token)
    if api_endpoint is None:
        raise Exception('[-] RPC server offline')

    print '[+] Received API endpoint: {}'.format(api_endpoint)

    profile_response = retrying_get_profile(service, access_token,
                                            api_endpoint, None)
    if profile_response is None or not profile_response.payload:
        raise Exception('Could not get profile')

    print '[+] Login successful'

    payload = profile_response.payload[0]
    profile = pokemon_pb2.ResponseEnvelop.ProfilePayload()
    profile.ParseFromString(payload)
    print '[+] Username: {}'.format(profile.profile.username)

    creation_time = \
        datetime.fromtimestamp(int(profile.profile.creation_time) / 1000)
    print '[+] You started playing Pokemon Go on: {}'.format(
        creation_time.strftime('%Y-%m-%d %H:%M:%S'))

    for curr in profile.profile.currency:
        print '[+] {}: {}'.format(curr.type, curr.amount)

    return api_endpoint, access_token, profile_response


def work(worker_no):
    times_done = 1

    # Login sequentially for PTC
    service = config.ACCOUNTS[worker_no][2]
    api_session = threading.local().api_session = requests.session()
    api_session.headers.update({'User-Agent': 'Niantic App'})
    api_session.verify = False

    api_endpoint, access_token, profile_response = login(
        username=config.ACCOUNTS[worker_no][0],
        password=config.ACCOUNTS[worker_no][1],
        service=service,
    )

    while times_done < 10:
        print('[W%d] Iteration %d' % (worker_no, times_done))
        main(worker_no, service, api_endpoint, access_token, profile_response)
        times_done += 1
        print('[W%d] Sleeping' % worker_no)
        time.sleep(60)
    start_worker(worker_no)


def main(worker_no, service, api_endpoint, access_token, profile_response):
    origin_lat, origin_lon = utils.get_start_coords(worker_no)

    args = get_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        print '[!] DEBUG mode on'

    steplimit = int(args.step_limit)

    pos = 1
    x = 0
    y = 0
    dx = 0
    dy = -1
    steplimit2 = steplimit**2
    session = db.Session()
    for step in range(steplimit2):
        add_to_db = []
        #starting at 0 index
        debug('looping: step {} of {}'.format((step+1), steplimit**2))
        # Scan location math
        if -steplimit2 / 2 < x <= steplimit2 / 2 and -steplimit2 / 2 < y <= steplimit2 / 2:
            lat = x * 0.0025 + origin_lat
            lon = y * 0.0025 + origin_lon
        if x == y or x < 0 and x == -y or x > 0 and x == 1 - y:
            (dx, dy) = (-dy, dx)

        (x, y) = (x + dx, y + dy)

        process_step(
            service,
            api_endpoint,
            access_token,
            profile_response,
            add_to_db=add_to_db,
            lat=lat,
            lon=lon,
        )

        for spawn_id in add_to_db:
            pokemon = pokemons[spawn_id]
            db.add_sighting(session, pokemon)
        session.commit()
        add_to_db = []
        print('Completed: ' + str(((step+1) + pos * .25 - .25) / (steplimit2) * 100) + '%')
    session.close()
    set_location_coords(origin_lat, origin_lon, 0)


def process_step(
    service, api_endpoint, access_token, profile_response, add_to_db, lat, lon
):
    print('[+] Searching for Pokemon at location {} {}'.format(lat, lon))
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
        hs.append(
            get_heartbeat(service, api_endpoint, access_token,
                          profile_response))
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
                # if cell.Fort:
                #     for Fort in cell.Fort:
                #         if Fort.Enabled == True:
                #             if Fort.GymPoints and args.display_gym:
                #                 gyms[Fort.FortId] = [Fort.Team, Fort.Latitude,
                #                                      Fort.Longitude, Fort.GymPoints]

                #             elif Fort.FortType \
                #                 and args.display_pokestop:
                #                 expire_time = 0
                #                 if Fort.LureInfo.LureExpiresTimestampMs:
                #                     expire_time = datetime\
                #                         .fromtimestamp(Fort.LureInfo.LureExpiresTimestampMs / 1000.0)\
                #                         .strftime("%H:%M:%S")
                #                 if (expire_time != 0 or not args.onlylure):
                #                     pokestops[Fort.FortId] = [Fort.Latitude,
                #                                               Fort.Longitude, expire_time]
        except AttributeError:
            break

    for poke in visible:
        disappear_timestamp = time.time() + poke.TimeTillHiddenMs / 1000
        pokemons[poke.SpawnPointId] = {
            "lat": poke.Latitude,
            "lng": poke.Longitude,
            "disappear_time": disappear_timestamp,
            "id": poke.pokemon.PokemonId,
        }
        add_to_db.append(poke.SpawnPointId)


def start_worker(worker_no):
    # Ok I NEED to global this here
    global workers
    print('[W%d] Worker (re)starting up!' % worker_no)
    worker = threading.Thread(target=work, args=[worker_no])
    worker.daemon = True
    worker.name = 'worker-%d' % worker_no
    worker.start()
    workers[worker_no] = worker


def spawn_workers(workers):
    count = config.GRID[0] * config.GRID[1]
    for worker_no in range(count):
        start_worker(worker_no)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    spawn_workers(workers)
