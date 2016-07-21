#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import smtplib

from peewee import Model, SqliteDatabase, InsertQuery, IntegerField,\
                   CharField, FloatField, BooleanField, DateTimeField
from datetime import datetime, timedelta
from base64 import b64encode

from .utils import get_pokemon_name, load_credentials
from .transform import transform_from_wgs_to_gcj
from pogom import config

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

db = SqliteDatabase('pogom.db')
log = logging.getLogger(__name__)

ACTIVE_RARES = {}

class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def get_all(cls):
        return [m for m in cls.select().dicts()]


class Pokemon(BaseModel):
    # We are base64 encoding the ids delivered by the api
    # because they are too big for sqlite to handle
    encounter_id = CharField(primary_key=True)
    spawnpoint_id = CharField()
    pokemon_id = IntegerField()
    latitude = FloatField()
    longitude = FloatField()
    disappear_time = DateTimeField()

    @classmethod
    def get_active(cls):
        query = (Pokemon
                 .select()
                 .where(Pokemon.disappear_time > datetime.utcnow())
                 .dicts())

        pokemons = []
        for p in query:
            p['pokemon_name'] = get_pokemon_name(p['pokemon_id'])
            pokemons.append(p)

        return pokemons


class Pokestop(BaseModel):
    pokestop_id = CharField(primary_key=True)
    enabled = BooleanField()
    latitude = FloatField()
    longitude = FloatField()
    last_modified = DateTimeField()
    lure_expiration = DateTimeField(null=True)
    active_pokemon_id = IntegerField(null=True)


class Gym(BaseModel):
    UNCONTESTED = 0
    TEAM_MYSTIC = 1
    TEAM_VALOR = 2
    TEAM_INSTINCT = 3

    gym_id = CharField(primary_key=True)
    team_id = IntegerField()
    guard_pokemon_id = IntegerField()
    gym_points = IntegerField()
    enabled = BooleanField()
    latitude = FloatField()
    longitude = FloatField()
    last_modified = DateTimeField()


def parse_map(map_dict):
    pokemons = {}
    pokestops = {}
    gyms = {}

    cells = map_dict['responses']['GET_MAP_OBJECTS']['map_cells']
    for cell in cells:
        for p in cell.get('wild_pokemons', []):

            pokemons[p['encounter_id']] = {
                'encounter_id': b64encode(str(p['encounter_id'])),
                'spawnpoint_id': p['spawnpoint_id'],
                'pokemon_id': p['pokemon_data']['pokemon_id'],
                'latitude': p['latitude'],
                'longitude': p['longitude'],
                'disappear_time': datetime.utcfromtimestamp(
                    (p['last_modified_timestamp_ms'] +
                     p['time_till_hidden_ms']) / 1000.0)
            }

        for f in cell.get('forts', []):
            if f.get('type') == 1:  # Pokestops
                    if 'lure_info' in f:
                        lure_expiration = datetime.utcfromtimestamp(
                            f['lure_info']['lure_expires_timestamp_ms'] / 1000.0)
                        active_pokemon_id = f['lure_info']['active_pokemon_id']
                    else:
                        lure_expiration, active_pokemon_id = None, None

                    pokestops[f['id']] = {
                        'pokestop_id': f['id'],
                        'enabled': f['enabled'],
                        'latitude': f['latitude'],
                        'longitude': f['longitude'],
                        'last_modified': datetime.utcfromtimestamp(
                            f['last_modified_timestamp_ms'] / 1000.0),
                        'lure_expiration': lure_expiration,
                        'active_pokemon_id': active_pokemon_id
                }

            else:  # Currently, there are only stops and gyms
                gyms[f['id']] = {
                    'gym_id': f['id'],
                    'team_id': f['owned_by_team'],
                    'guard_pokemon_id': f['guard_pokemon_id'],
                    'gym_points': f['gym_points'],
                    'enabled': f['enabled'],
                    'latitude': f['latitude'],
                    'longitude': f['longitude'],
                    'last_modified': datetime.utcfromtimestamp(
                        f['last_modified_timestamp_ms'] / 1000.0),
                }

    if pokemons:
        log.info("Upserting {} pokemon".format(len(pokemons)))
        bulk_upsert(Pokemon, pokemons)

    if pokestops:
        log.info("Upserting {} pokestops".format(len(pokestops)))
        bulk_upsert(Pokestop, pokestops)

    if gyms:
        log.info("Upserting {} gyms".format(len(gyms)))
        bulk_upsert(Gym, gyms)

def bulk_upsert(cls, data):
    num_rows = len(data.values())
    i = 0
    step = 120

    while i < num_rows:
        log.debug("Inserting items {} to {}".format(i, min(i+step, num_rows)))
        InsertQuery(cls, rows=data.values()[i:min(i+step, num_rows)]).upsert().execute()
        i+=step



def email_rare_pokemon():
    global ACTIVE_RARES
    rare_found = False
    POKEMANS = Pokemon.get_active(None)
    EMAIL_ADDRESS = config['GMAIL_USERNAME']
    EMAIL_PASS = config['GMAIL_PASSWORD']
    rare_pkmn = config['RARE_PKMN']
    time_offset = datetime.now() - datetime.utcnow()

    msg= MIMEMultipart('alternative')
    msg['Subject'] = 'Rare pokemon have been spotted near you!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    text = ""
    html = """\
        <html>
            <head></head>
                <body>"""
    for pkmn in POKEMANS:
        pokename = pkmn['pokemon_name']
        if pokename == u'Nidoran\u2642':
				    pokename = 'Nidoran-M'
        elif pokename == u'Nidoran\u2640':
            pokename = 'Nidoran-F'

        if pkmn['pokemon_name'] in rare_pkmn and pkmn['encounter_id'] not in ACTIVE_RARES.values():
            rare_found = True

            ACTIVE_RARES[pkmn['disappear_time']] = pkmn['encounter_id']
            bye_bye_time = pkmn['disappear_time'] + time_offset - timedelta(hours=1)
            zero_hour = bye_bye_time.strftime('%m:%M:%S %p')
            pkmn_map_link = "https://www.google.com/maps?q=%f,%f" % (pkmn['latitude'], pkmn['longitude'])
            text += "OMG a %s has been spotted near you!\n\nHere's a map: %s\n\nYou have until %s to catch %s.\n\n" % (pokename, pkmn_map_link, zero_hour, pokename)
            html += """\
                <p>OMG a %s has been spotted near you!</p>
                <p>Here's a map: <a href='%s'>HERE</a></p>
                <p>You have until %s to catch %s.</p>
                <br/>""" % (pkmn['pokemon_name'], pkmn_map_link, zero_hour, pkmn['pokemon_name'])
        
    if rare_found:
        rare_found = False
        text += "Happy hunting!"
        html += """\
				        <p>Happy hunting!</p>
            </body>
        </html>"""

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
			
        msg.attach(part1)
        msg.attach(part2)
        try:
            s= smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(EMAIL_ADDRESS, EMAIL_PASS)
            s.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
            print "Found rare pokemon. Sending email to %s." % EMAIL_ADDRESS
            s.quit()
        except smtplib.SMTPException:
            print "Found rare Pokemon but unable to send email. Check the map!"

    # cleaning expired Pokemon from rare list
    CLEAN_LIST = {}
    for timeleft in ACTIVE_RARES:
        if timeleft > datetime.utcnow():
            CLEAN_LIST[timeleft] = ACTIVE_RARES[timeleft]
    ACTIVE_RARES = CLEAN_LIST

def create_tables():
    db.connect()
    db.create_tables([Pokemon, Pokestop, Gym], safe=True)
    db.close()
