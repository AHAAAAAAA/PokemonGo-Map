from .utils import get_pokemon_rarity, get_pokemon_name
from pogom.utils import get_args
from datetime import datetime
from .custom_alerts.slackAlert import slackAlert
from slacker import Slacker
import yaml
import os
import smtplib

args = get_args()
alertpath = os.path.join(os.path.dirname(__file__), '../config/alerts.yaml')
with open(alertpath, 'r') as stream:
    try:
        doc = yaml.load(stream)
    except yaml.YAMLError as err:
        print(err)

alert_ignore = doc['ignore']
alert_only = doc['only']

if alert_only:
    alert_only = [x.lower().strip() for x in alert_only]
elif alert_ignore:
    alert_ignore = [x.lower().strip() for x in alert_ignore]


def customAlert(id, lat, lng, itime):
    pokemon_name = get_pokemon_name(id).lower()
    pokemon_rarity = get_pokemon_rarity(id).lower()
    pokemon_id = str(id)

    if alert_only:
        if pokemon_name in alert_only or pokemon_id in alert_only or pokemon_rarity in alert_only:
            doAlert = True
        else:
            doAlert = False
    elif alert_ignore:
        if pokemon_name in alert_ignore or pokemon_id in alert_ignore or pokemon_rarity in alert_ignore:
            doAlert = False
        else:
            doAlert = True

    if doAlert:
        if args.custom_alerts == 'slack':
            slackAlert(doc, pokemon_name, pokemon_rarity, pokemon_id, lat, lng, itime)
        if args.custom_alerts == 'email':
            emailAlert(doc, pokemon_name, pokemon_rarity, pokemon_id, lat, lng, itime)
