# encoding: utf-8

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import os
import re
import sys
import struct
import json
import time
import requests
import argparse
import threading

import werkzeug.serving

import pokemon_pb2

from google.protobuf.internal import encoder
from s2sphere import *
from datetime import datetime
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import ConnectionError
from requests.models import InvalidURL
from transform import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
PTC_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'
GOOGLEMAPS_KEY = "AIzaSyAZzeHhs-8JZ7i18MjFuM35dJHq70n3Hx4"

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

global_token = None
access_token = None
DEBUG = True
VERBOSE_DEBUG = False  # if you want to write raw request/response to the console
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0
deflat, deflng = 0, 0
default_step = 0.001
api_endpoint = None
pokemons = []
gyms = []
pokestops = []
numbertoteam = {0: "Gym", 1: "Mystic", 2: "Valor", 3: "Instinct"} # At least I'm pretty sure that's it. I could be wrong and then I'd be displaying the wrong owner team of gyms.


# stuff for in-background search thread
search_thread = None

def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string

def debug(message):
    if DEBUG:
        print('[-] {}'.format(message))

def time_left(ms):
    s = ms / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return h, m, s


def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)


def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)).parent(15)
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
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            debug("retrying_set_location: geocoder exception ({}), retrying".format(str(e)))
        time.sleep(1.25)


def set_location(location_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(location_name)
    print('[!] Your given location: {}'.format(loc.address.encode('utf-8')))
    print('[!] lat/long/alt: {} {} {}'.format(loc.latitude, loc.longitude, loc.altitude))
    global deflat
    global deflng
    deflat, deflng = loc.latitude, loc.longitude
    set_location_coords(loc.latitude, loc.longitude, loc.altitude)


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


def retrying_api_req(api_endpoint, access_token, *args, **kwargs):
    while True:
        try:
            response = api_req(api_endpoint, access_token, *args, **kwargs)
            if response:
                return response
            debug("retrying_api_req: api_req returned None, retrying")
        except (InvalidURL, ConnectionError) as e:
            debug("retrying_api_req: request error ({}), retrying".format(str(e)))
        time.sleep(1)


def api_req(api_endpoint, access_token, *args, **kwargs):
    p_req = pokemon_pb2.RequestEnvelop()
    p_req.rpc_id = 1469378659230941192

    p_req.unknown1 = 2

    p_req.latitude, p_req.longitude, p_req.altitude = get_location_coords()

    p_req.unknown12 = 989

    if 'useauth' not in kwargs or not kwargs['useauth']:
        p_req.auth.provider = 'ptc'
        p_req.auth.token.contents = access_token
        p_req.auth.token.unknown13 = 14
    else:
        p_req.unknown11.unknown71 = kwargs['useauth'].unknown71
        p_req.unknown11.unknown72 = kwargs['useauth'].unknown72
        p_req.unknown11.unknown73 = kwargs['useauth'].unknown73

    for arg in args:
        p_req.MergeFrom(arg)

    protobuf = p_req.SerializeToString()

    r = SESSION.post(api_endpoint, data=protobuf, verify=False)

    p_ret = pokemon_pb2.ResponseEnvelop()
    p_ret.ParseFromString(r.content)

    if VERBOSE_DEBUG:
        print("REQUEST:")
        print(p_req)
        print("Response:")
        print(p_ret)
        print("\n\n")
    time.sleep(0.51)
    return p_ret


def get_api_endpoint(access_token, api=API_URL):
    profile_response = None
    while not profile_response or not profile_response.api_url:
        debug("get_api_endpoint: calling get_profile")
        profile_response = get_profile(access_token, api, None)

    return ('https://%s/rpc' % profile_response.api_url)


def get_profile(access_token, api, useauth, *reqq):
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
    return retrying_api_req(api, access_token, req, useauth=useauth)


def login_ptc(username, password):
    print('[!] login for: {}'.format(username))
    head = {'User-Agent': 'Niantic App'}
    r = SESSION.get(LOGIN_URL, headers=head)
    if r is None:
        return render_template('nope.html', fullmap=fullmap)

    try:
        jdata = json.loads(r.content)
    except ValueError as e:
        debug("login_ptc: could not decode JSON from {}".format(r.content))
        return None

    data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': password,
    }
    r1 = SESSION.post(LOGIN_URL, data=data, headers=head)

    ticket = None
    try:
        ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
    except Exception as e:
        if DEBUG:
            print(r1.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': PTC_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = SESSION.post(LOGIN_OAUTH, data=data1)
    access_token = re.sub('&expires.*', '', r2.content)
    access_token = re.sub('.*access_token=', '', access_token)

    return access_token


def get_heartbeat(api_endpoint, access_token, response):
    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = "05daf51635c82611d1aac95c0b051d3ec088a930"
    m5.message = m.SerializeToString()
    walk = sorted(getNeighbors())
    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    m.lat = COORDS_LATITUDE
    m.long = COORDS_LONGITUDE
    m1.message = m.SerializeToString()
    response = get_profile(
        access_token,
        api_endpoint,
        response.unknown7,
        m1,
        pokemon_pb2.RequestEnvelop.Requests(),
        m4,
        pokemon_pb2.RequestEnvelop.Requests(),
        m5)
    if response is None:
        return
    payload = response.payload[0]
    heartbeat = pokemon_pb2.ResponseEnvelop.HeartbeatPayload()
    heartbeat.ParseFromString(payload)
    return heartbeat


def get_token(name, passw):
    """
    Get token if it's not None
    :return:
    :rtype:
    """
    global global_token
    if global_token is None:
        global_token = login_ptc(name, passw)
        return global_token
    else:
        return global_token


def main():
    debug("main")

    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    pokemonsJSON = json.load(open(path + '/pokemon.json'))

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="PTC Username", required=True)
    parser.add_argument("-p", "--password", help="PTC Password", required=True)
    parser.add_argument("-l", "--location", type=parse_unicode, help="Location", required=True)
    parser.add_argument("-st", "--step_limit", help="Steps", required=True)
    parser.add_argument("-i", "--ignore", help="Pokemon to ignore (comma separated)")
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-c", "--china", help="Coord Transformer for China", action='store_true')
    parser.set_defaults(DEBUG=True)
    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        print('[!] DEBUG mode on')

    retrying_set_location(args.location)

    access_token = get_token(args.username, args.password)
    if access_token is None:
        print('[-] Wrong username/password')
        return
    print('[+] RPC Session Token: {} ...'.format(access_token[:25]))

    api_endpoint = get_api_endpoint(access_token)
    if api_endpoint is None:
        print('[-] RPC server offline')
        return
    print('[+] Received API endpoint: {}'.format(api_endpoint))

    profile_response = get_profile(access_token, api_endpoint, None)
    if profile_response is None or not profile_response.payload:
        print('[-] Ooops...')
        raise Exception("Could not get profile")

    print('[+] Login successful')

    payload = profile_response.payload[0]
    profile = pokemon_pb2.ResponseEnvelop.ProfilePayload()
    profile.ParseFromString(payload)
    print('[+] Username: {}'.format(profile.profile.username))

    creation_time = datetime.fromtimestamp(int(profile.profile.creation_time) / 1000)
    print('[+] You started playing Pokemon Go on: {}'.format(
        creation_time.strftime('%Y-%m-%d %H:%M:%S'),
    ))

    for curr in profile.profile.currency:
        print('[+] {}: {}'.format(curr.type, curr.amount))

    origin = LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)
    steps = 0
    steplimit = int(args.step_limit)

    ignore = []
    if args.ignore:
        ignore = [i.lower().strip() for i in args.ignore.split(',')]

    pos = 1
    x   = 0
    y   = 0
    dx  = 0
    dy  = -1
    while steps < steplimit**2:
        debug("looping: step {} of {}".format(steps, steplimit**2))
        original_lat = FLOAT_LAT
        original_long = FLOAT_LONG
        parent = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)).parent(15)
        h = get_heartbeat(api_endpoint, access_token, profile_response)
        hs = [h]
        seen = set([])
        for child in parent.children():
            latlng = LatLng.from_point(Cell(child).get_center())
            set_location_coords(latlng.lat().degrees, latlng.lng().degrees, 0)
            hs.append(get_heartbeat(api_endpoint, access_token, profile_response))
        set_location_coords(original_lat, original_long, 0)
        visible = []
        for hh in hs:
            try:
                for cell in hh.cells:
                    for wild in cell.WildPokemon:
                        hash = wild.SpawnPointId + ':' + str(wild.pokemon.PokemonId)
                        if (hash not in seen):
                            visible.append(wild)
                            seen.add(hash)
                    if cell.Fort:
                        for Fort in cell.Fort:
                            if Fort.Enabled == True:
                                if args.china:
                                    Fort.Latitude, Fort.Longitude = transform_from_wgs_to_gcj(Location(Fort.Latitude, Fort.Longitude))
                                if Fort.GymPoints:
                                    gyms.append([Fort.Team, Fort.Latitude, Fort.Longitude])
                                elif Fort.FortType:
                                    pokestops.append([Fort.Latitude, Fort.Longitude])
            except AttributeError:
                break
        for poke in visible:
            pokename = pokemonsJSON[poke.pokemon.PokemonId - 1]['Name']
            if args.ignore:
                if pokename.lower() in ignore: continue
            other = LatLng.from_degrees(poke.Latitude, poke.Longitude)
            diff = other - origin
            # print(diff)
            difflat = diff.lat().degrees
            difflng = diff.lng().degrees
            time_to_hidden = poke.TimeTillHiddenMs
            left = '%d hours %d minutes %d seconds' % time_left(time_to_hidden)
            remaining = '%s remaining' % (left)
            pid = str(poke.pokemon.PokemonId)
            label = (
                        '<div style=\'position:float; top:0;left:0;\'><small><a href=\'http://www.pokemon.com/us/pokedex/'+pid+'\' target=\'_blank\' title=\'View in Pokedex\'>#'+pid+'</a></small> - <b>'+pokemonsJSON[poke.pokemon.PokemonId - 1]['Name']+'</b></div>'
                        '<center>'+remaining.replace('0 hours ','').replace('0 minutes ','')+'</center>'
                    )
            if args.china:
                poke.Latitude, poke.Longitude = transform_from_wgs_to_gcj(Location(poke.Latitude, poke.Longitude))
            pokemons.append([poke.pokemon.PokemonId, label, poke.Latitude, poke.Longitude])

        #Scan location math
        if (-steplimit/2 < x <= steplimit/2) and (-steplimit/2 < y <= steplimit/2):
            set_location_coords((x * 0.0025) + deflat, (y * 0.0025 ) + deflng, 0)
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
        steps +=1
        print("Completed:", ((steps + (pos * .25) - .25) / steplimit**2) * 100, "%")

    register_background_thread()


def register_background_thread(initial_registration=False):
    """
    Start a background thread to search for Pokemon
    while Flask is still able to serve requests for the map
    :param initial_registration: True if first registration and thread should start immediately, False if it's being called by the finishing thread to schedule a refresh
    :return: None
    """

    debug("register_background_thread called")
    global search_thread

    if initial_registration:
        if not werkzeug.serving.is_running_from_reloader():
            debug("register_background_thread: not running inside Flask so not starting thread")
            return
        if search_thread:
            debug("register_background_thread: initial registration requested but thread already running")
            return

        debug("register_background_thread: initial registration")
        search_thread = threading.Thread(target=main)

    else:
        debug("register_background_thread: queueing")
        search_thread = threading.Timer(30, main)  # delay, in seconds

    search_thread.daemon = True
    search_thread.name = "search_thread"
    search_thread.start()


def create_app():
    app = Flask(__name__, template_folder="templates")

    GoogleMaps(app, key=GOOGLEMAPS_KEY)
    return app

app = create_app()


@app.route('/')
def fullmap():
    pokeMarkers = []
    for pokemon in pokemons:
        currLat, currLon = pokemon[-2], pokemon[-1]
        imgnum = str(pokemon[0]);
        if len(imgnum) <= 2: imgnum = '0' + imgnum
        if len(imgnum) <= 2: imgnum = '0' + imgnum
        pokeMarkers.append(
            {
                'icon': 'static/icons/'+str(pokemon[0])+'.png',
                'lat': currLat,
                'lng': currLon,
                'infobox': pokemon[1]
                })
    for gym in gyms:
        if gym[0] == 0: color = "white"
        if gym[0] == 1: color = "rgba(0, 0, 256, .1)"
        if gym[0] == 2: color = "rgba(255, 0, 0, .1)"
        if gym[0] == 3: color = "rgba(255, 255, 0, .1)"
        pokeMarkers.append(
            {
                'icon': 'static/forts/'+numbertoteam[gym[0]]+'.png',
                'lat': gym[1],
                'lng': gym[2],
                'infobox': "<div style='background: "+color+"'>Gym owned by Team " + numbertoteam[gym[0]]
            })
    for stop in pokestops:
        pokeMarkers.append(
            {
                'icon': 'static/forts/Pstop.png',
                'lat': stop[0],
                'lng': stop[1],
                'infobox': "Pokestop"
            })
    fullmap = Map(
        identifier="fullmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=deflat,
        lng=deflng,
        markers=pokeMarkers,
        zoom="15"
    )
    return render_template('example_fullmap.html', fullmap=fullmap)


if __name__ == "__main__":
    register_background_thread(initial_registration=True)
    app.run(debug=True, threaded=True)
