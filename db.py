from datetime import datetime
import json
import time

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import not_


with open('locales/pokemon.en.json') as f:
    pokemon_names = json.load(f)


try:
    import config
    DB_ENGINE = config.DB_ENGINE
except ImportError, AttributeError:
    DB_ENGINE = 'sqlite:///db.sqlite'


def get_engine():
    return create_engine(DB_ENGINE)

Base = declarative_base()


class SightingCache(object):
    """Simple cache for storing actual sightings

    It's used in order not to make as many queries to the database.
    It's also capable of purging old entries.
    """
    def __init__(self):
        self.store = {}

    @staticmethod
    def _make_key(sighting):
        return (
            sighting.pokemon_id,
            sighting.spawn_id,
            sighting.normalized_timestamp,
            sighting.lat,
            sighting.lon,
        )

    def add(self, sighting):
        self.store[self._make_key(sighting)] = sighting.expire_timestamp

    def __contains__(self, sighting):
        expire_timestamp = self.store.get(self._make_key(sighting))
        if not expire_timestamp:
            return False
        timestamp_in_range = (
            expire_timestamp > sighting.expire_timestamp - 5 and
            expire_timestamp < sighting.expire_timestamp + 5
        )
        return timestamp_in_range

    def clean_expired(self):
        to_remove = []
        for key, timestamp in self.store.items():
            if timestamp < time.time() - 120:
                to_remove.append(key)
        for key in to_remove:
            del self.store[key]

CACHE = SightingCache()


class Sighting(Base):
    __tablename__ = 'sightings'

    id = Column(Integer, primary_key=True)
    pokemon_id = Column(Integer)
    spawn_id = Column(String(32))
    expire_timestamp = Column(Integer)
    normalized_timestamp = Column(Integer)
    lat = Column(String(16))
    lon = Column(String(16))


Session = sessionmaker(bind=get_engine())


def normalize_timestamp(timestamp):
    return int(float(timestamp) / 120.0) * 120


def add_sighting(session, pokemon):
    obj = Sighting(
        pokemon_id=pokemon['pokemon_id'],
        spawn_id=pokemon['spawn_id'],
        expire_timestamp=pokemon['expire_timestamp'],
        normalized_timestamp=normalize_timestamp(pokemon['expire_timestamp']),
        lat=pokemon['lat'],
        lon=pokemon['lon'],
    )
    # Check if there isn't the same entry already
    if obj in CACHE:
        return
    existing = session.query(Sighting) \
        .filter(Sighting.pokemon_id == obj.pokemon_id) \
        .filter(Sighting.spawn_id == obj.spawn_id) \
        .filter(Sighting.expire_timestamp > obj.expire_timestamp - 10) \
        .filter(Sighting.expire_timestamp < obj.expire_timestamp + 10) \
        .filter(Sighting.lat == obj.lat) \
        .filter(Sighting.lon == obj.lon) \
        .first()
    if existing:
        return
    session.add(obj)
    CACHE.add(obj)


def get_sightings(session):
    query = session.query(Sighting) \
        .filter(Sighting.expire_timestamp > time.time())
    trash_list = getattr(config, 'TRASH_IDS', None)
    if trash_list:
        query = query.filter(not_(Sighting.pokemon_id.in_(config.TRASH_IDS)))
    return query.all()


def get_session_stats(session):
    min_max_query = session.execute('''
        SELECT
            MIN(expire_timestamp) ts_min,
            MAX(expire_timestamp) ts_max,
            COUNT(*)
        FROM `sightings`;
    ''')
    min_max_result = min_max_query.first()
    length_hours = (min_max_result[1] - min_max_result[0]) // 3600
    # Convert to datetime
    return {
        'start': datetime.fromtimestamp(min_max_result[0]),
        'end': datetime.fromtimestamp(min_max_result[1]),
        'count': min_max_result[2],
        'length_hours': length_hours,
        'per_hour': min_max_result[2] / length_hours,
    }


def get_punch_card(session):
    query = session.execute('''
        SELECT
            CAST((expire_timestamp / 300) AS SIGNED) ts_date,
            COUNT(*) how_many
        FROM `sightings`
        GROUP BY ts_date ORDER BY ts_date
    ''')
    results = query.fetchall()
    results_dict = {r[0]: r[1] for r in results}
    filled = []
    for row_no, i in enumerate(range(int(results[0][0]), int(results[-1][0]))):
        item = results_dict.get(i)
        filled.append((row_no, item if item else 0))
    return filled


def get_top_pokemon(session, count=30, order='DESC'):
    query = session.execute('''
        SELECT
            pokemon_id,
            COUNT(*) how_many
        FROM sightings
        GROUP BY pokemon_id
        ORDER BY how_many {order}
        LIMIT {count}
    '''.format(order=order, count=count))
    return query.fetchall()


def get_stage2_pokemon(session):
    result = []
    if not hasattr(config, 'STAGE2'):
        return []
    for pokemon_id in config.STAGE2:
        count = session.query(Sighting) \
            .filter(Sighting.pokemon_id == pokemon_id) \
            .count()
        if count > 0:
            result.append((pokemon_id, count))
    return result


def get_nonexistent_pokemon(session):
    result = []
    query = session.execute('''
        SELECT DISTINCT pokemon_id FROM sightings
    ''')
    db_ids = [r[0] for r in query.fetchall()]
    for pokemon_id in range(1, 152):
        if pokemon_id not in db_ids:
            result.append(pokemon_id)
    return result


def get_all_sightings(session, pokemon_ids):
    # TODO: rename this and get_sightings
    query = session.query(Sighting) \
        .filter(Sighting.pokemon_id.in_(pokemon_ids)) \
        .all()
    return query
