import time

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import not_


try:
    import config
    DB_ENGINE = config.DB_ENGINE
except ImportError, AttributeError:
    DB_ENGINE = 'sqlite:///db.sqlite'


def get_engine():
    return create_engine(DB_ENGINE)

Base = declarative_base()


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


def add_sighting(session, spawn_id, pokemon):
    obj = Sighting(
        pokemon_id=pokemon['id'],
        spawn_id=spawn_id,
        expire_timestamp=pokemon['disappear_time'],
        normalized_timestamp=normalize_timestamp(pokemon['disappear_time']),
        lat=pokemon['lat'],
        lon=pokemon['lng'],
    )
    # Check if there isn't the same entry already
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


def get_sightings(session):
    return session.query(Sighting) \
        .filter(not_(Sighting.pokemon_id.in_(config.TRASH_IDS))) \
        .filter(Sighting.expire_timestamp > time.time()) \
        .all()
