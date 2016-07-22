# -*- coding: utf-8 -*-

__author__ = 'ufian'

import os
import logging
import time
import datetime
import telepot

from threading import Thread

from pogom import config
from pogom.app import Pogom
from pogom.utils import get_args, insert_mock_data, load_credentials
from pogom.search import search_loop, api, login, send_map_request, parse_map
from pogom.models import create_tables, Pokemon, Pokestop, Gym

from pogom.pgoapi.utilities import get_pos_by_name

import math

log = logging.getLogger(__name__)

search_thread = Thread()

SIZE_X = 0.0015
SIZE_Y = 0.0011


def dist(pos1, pos2):
    return math.fabs(pos1[0] - pos2[0]) < SIZE_Y and math.fabs(pos1[1] - pos2[1]) < SIZE_X

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')

    logging.getLogger("peewee").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
    logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    args = get_args()

    if args.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)

    create_tables()

    aposition = get_pos_by_name(args.location)

    config['ORIGINAL_LATITUDE'] = aposition[0]
    config['ORIGINAL_LONGITUDE'] = aposition[1]
    config['LOCALE'] = args.locale

    position = (config['ORIGINAL_LATITUDE'], config['ORIGINAL_LONGITUDE'], 0)

    login(args, position)
    
    failed_consecutive = 0
    
    
    bot = telepot.Bot(args.telegram)

    def get_image(lat, long):
        apos = (lat, long)
        response_dict = send_map_request(api, (lat, long, 0))
        
        #print response_dict
        cells = response_dict['responses']['GET_MAP_OBJECTS']['map_cells']
        
        pokemons = []
        pokestors = []
        gyms = []
        
        for cell in cells:
            for p in cell.get('wild_pokemons', []):
                d_t = ((p['last_modified_timestamp_ms'] + p['time_till_hidden_ms']) / 1000.0)
                
                pokemons.append((
                    p['latitude'],
                    p['longitude'],
                    p['pokemon_data']['pokemon_id'],
                    d_t
                ))
        
            for f in cell.get('forts', []):
                if f.get('type') == 1:  # Pokestops
                    if 'lure_info' in f:
                        lure_expiration = f['lure_info']['lure_expires_timestamp_ms'] / 1000.0
                        active_pokemon_id = f['lure_info']['active_pokemon_id']
                    else:
                        lure_expiration, active_pokemon_id = None, None
                    
                    pokestors.append((
                        f['latitude'],
                        f['longitude'],
                        lure_expiration,
                        active_pokemon_id
                    ))
    
                else:  # Currently, there are only stops and gyms
                    gyms.append((
                        f['latitude'],
                        f['longitude'],
                        f.get('owned_by_team')
                    ))
                        
        
        
        from staticmap import StaticMap, CircleMarker, IconMarker
        m = StaticMap(600, 600)
        
        m.add_marker(CircleMarker((apos[1] + SIZE_X,  apos[0] + SIZE_Y), '#FF00FF', 1))
        m.add_marker(CircleMarker((apos[1] - SIZE_X,  apos[0] + SIZE_Y), '#FF00FF', 1))
        m.add_marker(CircleMarker((apos[1] + SIZE_X,  apos[0] - SIZE_Y), '#FF00FF', 1))
        m.add_marker(CircleMarker((apos[1] - SIZE_X,  apos[0] - SIZE_Y), '#FF00FF', 1))
        
        for p in pokemons:
            m.add_marker(IconMarker((p[1], p[0]), 'static/icons/{}.png'.format(p[2]), 0, 0))
    
        for p in pokestors:
            if dist(apos, p):
                m.add_marker(CircleMarker((p[1], p[0]), '#00FF00', 9))
    
        for p in gyms:
            if dist(apos, p):
                m.add_marker(CircleMarker((p[1], p[0]), '#FF0000', 9))
    
        
        image = m.render(zoom=18)
        image.save('marker.png')
        


    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
    
        if content_type == 'location':
            try:
                get_image(msg['location']['latitude'], msg['location']['longitude'])
                bot.sendPhoto(chat_id, open('marker.png', 'rb'))
            except Exception as e:
                print repr(e)
                bot.sendMessage(chat_id, u'Неведомая хрень:\n' + repr(e))

    bot.message_loop(handle)
    
    while 1:
        time.sleep(10)
