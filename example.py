#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_googlemaps import icons
import os
import re
import sys
import struct
import json
import requests
import argparse
import getpass
import threading
import werkzeug.serving
import pokemon_pb2
import time
from google.protobuf.internal import encoder
from google.protobuf.message import DecodeError
from s2sphere import *
from datetime import datetime
from geopy.geocoders import GoogleV3
from gpsoauth import perform_master_login, perform_oauth
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import ConnectionError
from requests.models import InvalidURL
from transform import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = \
    'https://sso.pokemon.com/sso/login?service=https://sso.pokemon.com/sso/oauth2.0/callbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
APP = 'com.nianticlabs.pokemongo'

with open('credentials.json') as _file:
    credentials = json.load(_file)

PTC_CLIENT_SECRET = credentials.get('ptc_client_secret', None)
ANDROID_ID = credentials.get('android_id', None)
SERVICE = credentials.get('service', None)
CLIENT_SIG = credentials.get('client_sig', None)
GOOGLE_MAPS_KEY = credentials.get('gmaps_key', None)

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

global_password = None
global_token = None
access_token = None
DEBUG = True
VERBOSE_DEBUG = False  # if you want to write raw request/response to the console
COORDINATES_LATITUDE = 0
COORDINATES_LONGITUDE = 0
COORDINATES_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0
NEXT_LAT = 0
NEXT_LONG = 0
auto_refresh = 0
default_step = 0.001
api_endpoint = None
pokemons = {}
gyms = {}
pokestops = {}
number_to_team = {
    # At least I'm pretty sure that's it. I could be wrong and then I'd be displaying the wrong owner team of gyms.
    0: 'Gym',
    1: 'Mystic',
    2: 'Valor',
    3: 'Instinct',
}
origin_lat, origin_lon = int, int
is_ampm_clock = False

# stuff for in-background search thread

search_thread = None


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


def parse_unicode(byte_string):
    decoded_string = byte_string.decode(sys.getfilesystemencoding())
    return decoded_string


def debug(message):
    if DEBUG:
        print '[-] {}'.format(message)


def time_left(ms):
    s = ms / 1000
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)
    return h, m, s


def encode(cell_id):
    output = []
    encoder._VarintEncoder()(output.append, cell_id)
    return ''.join(output)


def get_neighbors():
    _origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT,
                                                      FLOAT_LONG)).parent(15)
    walk = [_origin.id()]

    # 10 before and 10 after

    _next = _origin.next()
    prev = _origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(_next.id())
        _next = _next.next()
        prev = prev.prev()
    return walk


def f2i(_float):
    return struct.unpack('<Q', struct.pack('<d', _float))[0]


def f2h(_float):
    return hex(struct.unpack('<Q', struct.pack('<d', _float))[0])


def h2f(_hex):
    return struct.unpack('<d', struct.pack('<Q', int(_hex, 16)))[0]


def retrying_set_location(location_name):
    """
    Continue trying to get co-ords from Google Location until we have them
    :param location_name: string to pass to Location API
    :return: None
    """

    while True:
        try:
            set_location(location_name)
            return
        except (GeocoderTimedOut, GeocoderServiceError), e:
            debug(
                'retrying_set_location: geocoder exception ({}), retrying'.format(
                    str(e)))
        time.sleep(1.25)


def set_location(location_name):
    geolocator = GoogleV3()
    prog = re.compile('^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$')
    global origin_lat
    global origin_lon
    if prog.match(location_name):
        local_lat, local_lng = [float(x) for x in location_name.split(",")]
        alt = 0
        origin_lat, origin_lon = local_lat, local_lng
    else:
        loc = geolocator.geocode(location_name)
        origin_lat, origin_lon = local_lat, local_lng = loc.latitude, loc.longitude
        alt = loc.altitude
        print '[!] Your given location: {}'.format(loc.address.encode('utf-8'))

    print('[!] lat/long/alt: {} {} {}'.format(local_lat, local_lng, alt))
    set_location_coordinates(local_lat, local_lng, alt)


def set_location_coordinates(lat, _long, alt):
    global COORDINATES_LATITUDE, COORDINATES_LONGITUDE, COORDINATES_ALTITUDE
    global FLOAT_LAT, FLOAT_LONG
    FLOAT_LAT = lat
    FLOAT_LONG = _long
    COORDINATES_LATITUDE = f2i(lat)  # 0x4042bd7c00000000 # f2i(lat)
    COORDINATES_LONGITUDE = f2i(_long)  # 0xc05e8aae40000000 #f2i(long)
    COORDINATES_ALTITUDE = f2i(alt)


def get_location_coordinates():
    return COORDINATES_LATITUDE, COORDINATES_LONGITUDE, COORDINATES_ALTITUDE


def retrying_api_req(service, _api_endpoint, _access_token, *args, **kwargs):
    while True:
        try:
            response = api_req(service, _api_endpoint, _access_token, *args,
                               **kwargs)
            if response:
                return response
            debug('retrying_api_req: api_req returned None, retrying')
        except (InvalidURL, ConnectionError, DecodeError), e:
            debug('retrying_api_req: request error ({}), retrying'.format(
                str(e)))
        time.sleep(1)


def api_req(service, _api_endpoint, _access_token, *args, **kwargs):
    p_req = pokemon_pb2.RequestEnvelop()
    p_req.rpc_id = 1469378659230941192

    p_req.unknown1 = 2

    (p_req.latitude, p_req.longitude, p_req.altitude) = \
        get_location_coordinates()

    p_req.unknown12 = 989

    if 'useauth' not in kwargs or not kwargs['useauth']:
        p_req.auth.provider = service
        p_req.auth.token.contents = _access_token
        p_req.auth.token.unknown13 = 14
    else:
        p_req.unknown11.unknown71 = kwargs['useauth'].unknown71
        p_req.unknown11.unknown72 = kwargs['useauth'].unknown72
        p_req.unknown11.unknown73 = kwargs['useauth'].unknown73

    for arg in args:
        p_req.MergeFrom(arg)

    proto_buf = p_req.SerializeToString()

    r = SESSION.post(_api_endpoint, data=proto_buf, verify=False)

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


def get_api_endpoint(service, _access_token, api=API_URL):
    profile_response = None
    while not profile_response:
        profile_response = retrying_get_profile(service, _access_token, api,
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


def retrying_get_profile(service, _access_token, api, use_auth, *reqq):
    profile_response = None
    while not profile_response:
        profile_response = get_profile(service, _access_token, api, use_auth,
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


def get_profile(service, _access_token, api, use_auth, *reqq):
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
    return retrying_api_req(service, api, _access_token, req, useauth=use_auth)


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
    r = SESSION.get(LOGIN_URL, headers=head)
    if r is None:
        return render_template('nope.html', fullmap=fullmap)

    try:
        jdata = json.loads(r.content)
    except ValueError:
        debug('login_ptc: could not decode JSON from {}'.format(r.content))
        return None

    # Maximum password length is 15 (sign in page enforces this limit, API does not)

    if len(password) > 15:
        print '[!] Trimming password to 15 characters'
        password = password[:15]

    _data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': password,
    }
    r1 = SESSION.post(LOGIN_URL, data=_data, headers=head)

    try:
        ticket = re.sub(".*ticket=", '', r1.history[0].headers['Location'])
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
    r2 = SESSION.post(LOGIN_OAUTH, data=data1)
    access = re.sub("&expires.*", '', r2.content)
    _access_token = re.sub(".*access_token=", '', access)

    return _access_token


def get_heartbeat(service,
                  _api_endpoint,
                  _access_token,
                  response, ):
    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = '05daf51635c82611d1aac95c0b051d3ec088a930'
    m5.message = m.SerializeToString()
    walk = sorted(get_neighbors())
    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = \
        "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    m.lat = COORDINATES_LATITUDE
    m.long = COORDINATES_LONGITUDE
    m1.message = m.SerializeToString()
    response = get_profile(service,
                           _access_token,
                           _api_endpoint,
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

    global global_token
    if global_token is None:
        if service == 'ptc':
            global_token = login_ptc(username, password)
        else:
            global_token = login_google(username, password)
        return global_token
    else:
        return global_token


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--auth_service', type=str.lower, help='Auth Service', default='ptc')
    parser.add_argument('-u', '--username', help='Username', required=True)
    parser.add_argument('-p', '--password', help='Password', required=False)
    parser.add_argument(
        '-l', '--location', type=parse_unicode, help='Location', required=True)
    parser.add_argument('-st', '--step-limit', help='Steps', required=True)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-i', '--ignore', help='Comma-separated list of Pokémon names to ignore')
    group.add_argument(
        '-o', '--only', help='Comma-separated list of Pokémon names to search')
    parser.add_argument(
        "-ar",
        "--auto_refresh",
        help="Enables an auto-refresh that behaves the same as a page reload. " +
             "Needs an integer value for the amount of seconds")
    parser.add_argument(
        '-dp',
        '--display-pokestop',
        help='Display pokéstop',
        action='store_true',
        default=False)
    parser.add_argument(
        '-dg',
        '--display-gym',
        help='Display Gym',
        action='store_true',
        default=False)
    parser.add_argument(
        '-H',
        '--host',
        help='Set web server listening host',
        default='127.0.0.1')
    parser.add_argument(
        '-P',
        '--port',
        type=int,
        help='Set web server listening port',
        default=5000)
    parser.add_argument(
        "-L",
        "--locale",
        help="Locale for Pokemon names: default en, check locale folder for more options",
        default="en")
    parser.add_argument(
        "-ol",
        "--onlylure",
        help='Display only lured pokéstop',
        action='store_true')
    parser.add_argument(
        '-c',
        '--china',
        help='Coordinates transformer for China',
        action='store_true')
    parser.add_argument(
        "-pm",
        "--ampm_clock",
        help="Toggles the AM/PM clock for Pokemon timers",
        action='store_true',
        default=False)
    parser.add_argument(
        '-d', '--debug', help='Debug Mode', action='store_true')
    parser.set_defaults(DEBUG=True)
    return parser.parse_args()


@memoize
def login(_args):
    global global_password
    if not global_password:
        if _args.password:
            global_password = _args.password
        else:
            global_password = getpass.getpass()

    _access_token = get_token(_args.auth_service, _args.username, global_password)
    if _access_token is None:
        raise Exception('[-] Wrong username/password')

    print '[+] RPC Session Token: {} ...'.format(_access_token[:25])

    _api_endpoint = get_api_endpoint(_args.auth_service, _access_token)
    if _api_endpoint is None:
        raise Exception('[-] RPC server offline')

    print '[+] Received API endpoint: {}'.format(_api_endpoint)

    profile_response = retrying_get_profile(_args.auth_service, _access_token,
                                            _api_endpoint, None)
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

    return _api_endpoint, _access_token, profile_response


def main():
    full_path = os.path.realpath(__file__)
    (path, filename) = os.path.split(full_path)

    _args = get_args()

    if _args.auth_service not in ['ptc', 'google']:
        print '[!] Invalid Auth service specified'
        return

    print('[+] Locale is ' + _args.locale)
    pokemons_json = json.load(
        open(path + '/locales/pokemon.' + _args.locale + '.json'))

    if _args.debug:
        global DEBUG
        DEBUG = True
        print '[!] DEBUG mode on'

    # only get location for first run
    if not (FLOAT_LAT and FLOAT_LONG):
        print('[+] Getting initial location')
        retrying_set_location(_args.location)

    if _args.auto_refresh:
        global auto_refresh
        auto_refresh = int(_args.auto_refresh) * 1000

    if _args.ampm_clock:
        global is_ampm_clock
        is_ampm_clock = True

    _api_endpoint, _access_token, profile_response = login(_args)

    clear_stale_pokemons()

    step_limit = int(_args.step_limit)

    ignore = []
    only = []
    if _args.ignore:
        ignore = [i.lower().strip() for i in _args.ignore.split(',')]
    elif _args.only:
        only = [i.lower().strip() for i in _args.only.split(',')]

    pos = 1
    x = 0
    y = 0
    dx = 0
    dy = -1
    step_limit2 = step_limit ** 2
    for step in range(step_limit2):
        # starting at 0 index
        debug('looping: step {} of {}'.format((step + 1), step_limit ** 2))
        # debug('steplimit: {} x: {} y: {} pos: {} dx: {} dy {}'.format(steplimit2, x, y, pos, dx, dy))
        # Scan location math
        if -step_limit2 / 2 < x <= step_limit2 / 2 and -step_limit2 / 2 < y <= step_limit2 / 2:
            set_location_coordinates(x * 0.0025 + origin_lat, y * 0.0025 + origin_lon, 0)
        if x == y or x < 0 and x == -y or x > 0 and x == 1 - y:
            (dx, dy) = (-dy, dx)

        (x, y) = (x + dx, y + dy)

        process_step(_args, _api_endpoint, _access_token, profile_response, pokemons_json, ignore, only)

        print('Completed: ' + str(
            ((step + 1) + pos * .25 - .25) / step_limit2 * 100) + '%')

    global NEXT_LAT, NEXT_LONG
    if (NEXT_LAT and NEXT_LONG and
            (NEXT_LAT != FLOAT_LAT or NEXT_LONG != FLOAT_LONG)):
        print('Update to next location %f, %f' % (NEXT_LAT, NEXT_LONG))
        set_location_coordinates(NEXT_LAT, NEXT_LONG, 0)
        NEXT_LAT = 0
        NEXT_LONG = 0
    else:
        set_location_coordinates(origin_lat, origin_lon, 0)

    register_background_thread()


def process_step(_args, _api_endpoint, _access_token, profile_response,
                 pokemons_json, ignore, only):
    print('[+] Searching pokemons for location {} {}'.format(FLOAT_LAT, FLOAT_LONG))
    # origin = LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)
    step_lat = FLOAT_LAT
    step_long = FLOAT_LONG
    parent = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT,
                                                     FLOAT_LONG)).parent(15)
    h = get_heartbeat(_args.auth_service, _api_endpoint, _access_token, profile_response)
    hs = [h]
    seen = set([])

    for child in parent.children():
        latlng = LatLng.from_point(Cell(child).get_center())
        set_location_coordinates(latlng.lat().degrees, latlng.lng().degrees, 0)
        hs.append(
            get_heartbeat(_args.auth_service, _api_endpoint, _access_token,
                          profile_response))
    set_location_coordinates(step_lat, step_long, 0)
    visible = []

    for hh in hs:
        try:
            for cell in hh.cells:
                for wild in cell.WildPokemon:
                    _hash = wild.SpawnPointId + ':' \
                            + str(wild.pokemon.PokemonId)
                    if _hash not in seen:
                        visible.append(wild)
                        seen.add(_hash)
                if cell.Fort:
                    for Fort in cell.Fort:
                        if Fort.Enabled:
                            if _args.china:
                                (Fort.Latitude, Fort.Longitude) = \
                                    transform_from_wgs_to_gcj(Location(Fort.Latitude, Fort.Longitude))
                            if Fort.GymPoints and _args.display_gym:
                                gyms[Fort.FortId] = [Fort.Team, Fort.Latitude,
                                                     Fort.Longitude, Fort.GymPoints]

                            elif Fort.FortType \
                                    and _args.display_pokestop:
                                expire_time = 0
                                if Fort.LureInfo.LureExpiresTimestampMs:
                                    expire_time = datetime \
                                        .fromtimestamp(Fort.LureInfo.LureExpiresTimestampMs / 1000.0) \
                                        .strftime("%H:%M:%S")
                                if expire_time != 0 or not _args.onlylure:
                                    pokestops[Fort.FortId] = [Fort.Latitude,
                                                              Fort.Longitude, expire_time]
        except AttributeError:
            break

    for poke in visible:
        poke_name = pokemons_json[str(poke.pokemon.PokemonId)]
        if _args.ignore:
            if poke_name.lower() in ignore:
                continue
        elif _args.only:
            if poke_name.lower() not in only:
                continue

        disappear_timestamp = time.time() + poke.TimeTillHiddenMs / 1000

        if _args.china:
            (poke.Latitude, poke.Longitude) = \
                transform_from_wgs_to_gcj(Location(poke.Latitude,
                                                   poke.Longitude))

        pokemons[poke.SpawnPointId] = {
            "lat": poke.Latitude,
            "lng": poke.Longitude,
            "disappear_time": disappear_timestamp,
            "id": poke.pokemon.PokemonId,
            "name": poke_name
        }


def clear_stale_pokemons():
    current_time = time.time()

    for pokemon_key in pokemons.keys():
        pokemon = pokemons[pokemon_key]
        if current_time > pokemon['disappear_time']:
            print "[+] removing stale pokemon %s at %f, %f from list" % (
                pokemon['name'].encode('utf-8'), pokemon['lat'], pokemon['lng'])
            del pokemons[pokemon_key]


def register_background_thread(initial_registration=False):
    """
    Start a background thread to search for Pokemon
    while Flask is still able to serve requests for the map
    :param initial_registration: True if first registration and thread should start immediately,
    False if it's being called by the finishing thread to schedule a refresh
    :return: None
    """

    debug('register_background_thread called')
    global search_thread

    if initial_registration:
        if not werkzeug.serving.is_running_from_reloader():
            debug(
                'register_background_thread: not running inside Flask so not starting thread')
            return
        if search_thread:
            debug(
                'register_background_thread: initial registration requested but thread already running')
            return

        debug('register_background_thread: initial registration')
        search_thread = threading.Thread(target=main)

    else:
        debug('register_background_thread: queueing')
        search_thread = threading.Timer(30, main)  # delay, in seconds

    search_thread.daemon = True
    search_thread.name = 'search_thread'
    search_thread.start()


def create_app():
    _app = Flask(__name__, template_folder='templates')

    GoogleMaps(_app, key=GOOGLE_MAPS_KEY)
    return _app


app = create_app()


@app.route('/data')
def data():
    """ Gets all the PokeMarkers via REST """
    return json.dumps(get_pokemarkers())


@app.route('/raw_data')
def raw_data():
    """ Gets raw data for pokemons/gyms/pokestops via REST """
    return flask.jsonify(pokemons=pokemons, gyms=gyms, pokestops=pokestops)


@app.route('/config')
def config():
    """ Gets the settings for the Google Maps via REST"""
    center = {
        'lat': FLOAT_LAT,
        'lng': FLOAT_LONG,
        'zoom': 15,
        'identifier': "fullmap"
    }
    return json.dumps(center)


@app.route('/')
def fullmap():
    clear_stale_pokemons()

    return render_template(
        "example_fullmap.html", key=GOOGLE_MAPS_KEY, fullmap=get_map(), auto_refresh=auto_refresh)


@app.route('/next_loc')
def next_loc():
    global NEXT_LAT, NEXT_LONG

    lat = flask.request.args.get('lat', '')
    lon = flask.request.args.get('lon', '')
    if not (lat and lon):
        print('[-] Invalid next location: %s,%s' % (lat, lon))
    else:
        print('[+] Saved next location as %s,%s' % (lat, lon))
        NEXT_LAT = float(lat)
        NEXT_LONG = float(lon)
        return 'ok'


def get_pokemarkers():
    poke_markers = [{
        'icon': icons.dots.red,
        'lat': origin_lat,
        'lng': origin_lon,
        'infobox': "Start position",
        'type': 'custom',
        'key': 'start-position',
        'disappear_time': -1
    }]

    for pokemon_key in pokemons:
        pokemon = pokemons[pokemon_key]
        datestr = datetime.fromtimestamp(pokemon[
                                             'disappear_time'])
        date_output = datestr.strftime("%H:%M:%S")
        if is_ampm_clock:
            date_output = datestr.strftime("%I:%M%p").lstrip('0')
        pokemon['disappear_time_formatted'] = date_output

        label_tmpl = u'''
<div><b>{name}</b><span> - </span><small><a href='http://www.pokemon.com/us/pokedex/{id}' target='_blank'
title='View in Pokedex'>#{id}</a></small></div>
<div>Disappears at - {disappear_time_formatted} <span class='label-countdown'
disappears-at='{disappear_time}'></span></div>
<div><a href='https://www.google.com/maps/dir/Current+Location/{lat},{lng}' target='_blank' title='View in Maps'>
Get Directions</a></div>
'''
        label = label_tmpl.format(**pokemon)
        #  NOTE: `infobox` field doesn't render multiple line string in frontend
        label = label.replace('\n', '')

        poke_markers.append({
            'type': 'pokemon',
            'key': pokemon_key,
            'disappear_time': pokemon['disappear_time'],
            'icon': 'static/icons/%d.png' % pokemon["id"],
            'lat': pokemon["lat"],
            'lng': pokemon["lng"],
            'infobox': label
        })

    for gym_key in gyms:
        gym = gyms[gym_key]
        if gym[0] == 0:
            color = "rgba(0,0,0,.4)"
        elif gym[0] == 1:
            color = "rgba(0, 0, 256, .4)"
        elif gym[0] == 2:
            color = "rgba(255, 0, 0, .4)"
        elif gym[0] == 3:
            color = "rgba(255, 255, 0, .4)"
        else:
            color = None

        icon = 'static/forts/' + number_to_team[gym[0]] + '_large.png'
        poke_markers.append({
            'icon': 'static/forts/' + number_to_team[gym[0]] + '.png',
            'type': 'gym',
            'key': gym_key,
            'disappear_time': -1,
            'lat': gym[1],
            'lng': gym[2],
            'infobox': "<div><center><small>Gym owned by:</small><br><b style='color:" + color + "'>Team " +
                       number_to_team[gym[0]] + "</b><br><img id='" + number_to_team[
                           gym[0]] + "' height='100px' src='" + icon + "'><br>Prestige: " + str(gym[3]) + "</center>"
        })
    for stop_key in pokestops:
        stop = pokestops[stop_key]
        if stop[2] > 0:
            poke_markers.append({
                'type': 'lured_stop',
                'key': stop_key,
                'icon': 'static/forts/PstopLured.png',
                'lat': stop[0],
                'lng': stop[1],
                'infobox': 'Lured Pokestop, expires at ' + stop[2],
            })
        else:
            poke_markers.append({
                'type': 'stop',
                'key': stop_key,
                'disappear_time': -1,
                'icon': 'static/forts/Pstop.png',
                'lat': stop[0],
                'lng': stop[1],
                'infobox': 'Pokestop',
            })
    return poke_markers


def get_map():
    full_map = Map(
        identifier="fullmap2",
        style='height:100%;width:100%;top:0;left:0;position:absolute;z-index:200;',
        lat=origin_lat,
        lng=origin_lon,
        markers=get_pokemarkers(),
        zoom='15', )
    return full_map


if __name__ == '__main__':
    args = get_args()
    register_background_thread(initial_registration=True)
    app.run(debug=True, threaded=True, host=args.host, port=args.port)
