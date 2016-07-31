from .utils import get_pokemon_name
from pogom.utils import get_args
from datetime import datetime
import psycopg2
import random

# This code forks the data from PokemonGo-Map into the Pokelyzer database. For information on setting up Pokelyer, visit https://github.com/Brideau/pokelyzer

args = get_args()

conn = psycopg2.connect(dbname="pokemon_go", user="pokemon_go_role", password=args.pokel_pass, host="127.0.0.1")
conn.autocommit = True
cursor = conn.cursor()

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

    pokemon_go_era = args.pokel_era

    query =  "INSERT INTO spotted_pokemon (name, encounter_id, last_modified_time, time_until_hidden_ms, hidden_time_unix_s, hidden_time_utc, spawnpoint_id, longitude, latitude, pokemon_id, longitude_jittered, latitude_jittered, pokemon_go_era) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (encounter_id) DO UPDATE SET last_modified_time = EXCLUDED.last_modified_time, time_until_hidden_ms = EXCLUDED.time_until_hidden_ms, hidden_time_unix_s = EXCLUDED.hidden_time_unix_s, hidden_time_utc = EXCLUDED.hidden_time_utc;"

    data = (pokemon_name, encounter_id, last_modified_time, time_until_hidden_ms, hidden_time_unix_s, hidden_time_utc, spawnpoint_id, longitude, latitude, pokemon_id, longitude_jittered, latitude_jittered, pokemon_go_era)

    cursor.execute(query, data)
