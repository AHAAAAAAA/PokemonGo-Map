from .utils import get_pokemon_name
from pogom.utils import get_args
from datetime import datetime
import psycopg2
import random

args = get_args()
#temporarily disabling because -o and -i is removed from 51f651228c00a96b86f5c38d1a2d53b32e5d9862
#IGNORE = None
#ONLY = None
#if args.ignore:
#    IGNORE =  [i.lower().strip() for i in args.ignore.split(',')]
#elif args.only:
#    ONLY = [i.lower().strip() for i in args.only.split(',')]

conn = psycopg2.connect(dbname="pokemon_go", user="pokemon_go_role", password=args.pokel_pass, host="127.0.0.1")
conn.autocommit = True
cursor = conn.cursor()

def printPokemon(id,lat,lng,itime):
    if args.display_in_console:
        pokemon_name = get_pokemon_name(id).lower()
        pokemon_id = str(id)
        doPrint = True
        #if args.ignore:
        #    if pokemon_name in IGNORE or pokemon_id in IGNORE:
        #        doPrint = False
        #elif args.only:
        #    if pokemon_name not in ONLY and pokemon_id not in ONLY:
        #        doPrint = False
        if doPrint:
            timeLeft = itime-datetime.utcnow()
            print "======================================\n Name: %s\n Coord: (%f,%f)\n ID: %s \n Remaining Time: %s\n======================================" % (
                pokemon_name.encode('utf-8'),lat,lng,pokemon_id,str(timeLeft))

def logPokemonDb(p):
    pokemon_id = int(p['pokemon_data']['pokemon_id'])
    pokemon_name = get_pokemon_name(str(pokemon_id)).lower()

    last_modified_time = int(p['last_modified_timestamp_ms'])
    time_until_hidden_ms = int(p['time_till_hidden_ms'])

    hidden_time_unix_s = int((p['last_modified_timestamp_ms'] + p['time_till_hidden_ms']) / 1000.0)
    hidden_time_utc = datetime.utcfromtimestamp(hidden_time_unix_s)

    encounter_id = str(p['encounter_id'])
    spawnpoint_id = str(p['spawnpoint_id'])

    longitude = float(p['longitude'])
    latitude = float(p['latitude'])
    longitude_jittered = longitude + random.gauss(0, 0.3) * 0.0005
    latitude_jittered = latitude + random.gauss(0, 0.3) * 0.0005

    query =  "INSERT INTO spotted_pokemon (name, encounter_id, last_modified_time, time_until_hidden_ms, hidden_time_unix_s, hidden_time_utc, spawnpoint_id, longitude, latitude, pokemon_id, longitude_jittered, latitude_jittered) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (encounter_id) DO UPDATE SET last_modified_time = EXCLUDED.last_modified_time, time_until_hidden_ms = EXCLUDED.time_until_hidden_ms, hidden_time_unix_s = EXCLUDED.hidden_time_unix_s, hidden_time_utc = EXCLUDED.hidden_time_utc;"

    data = (pokemon_name, encounter_id, last_modified_time, time_until_hidden_ms, hidden_time_unix_s, hidden_time_utc, spawnpoint_id, longitude, latitude, pokemon_id, longitude_jittered, latitude_jittered)

    cursor.execute(query, data)
