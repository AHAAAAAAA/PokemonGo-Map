from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime

db = SqliteExtDatabase('pokemap.db')

class BaseModel(Model):
    class Meta:
        database = db

class Pokemon(BaseModel):
    spawnpoint_id = CharField(unique=True)
    pokedex_num = IntegerField()
    name = CharField()
    lat = FloatField()
    lon = FloatField()
    disappear_time = FloatField()

class Pokestop(BaseModel):
    pokestop_id = CharField(unique=True)
    lat = FloatField()
    lon = FloatField()

class Gym(BaseModel):
    gym_id = CharField(unique=True)
    team_id = IntegerField()
    team_name = CharField()
    lat = FloatField()
    lon = FloatField()
    

