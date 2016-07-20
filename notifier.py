import json
from pushbullet import Pushbullet
from geopy.geocoders import Nominatim
from datetime import datetime

pushbullet_client = None
wanted_pokemon = None

# Initialize object
def init():
    global pushbullet_client, wanted_pokemon
    # load pushbullet key
    with open('config.json') as data_file:
        data = json.load(data_file)
        # get list of pokemon to send notifications for
        wanted_pokemon = _str( data["notify"] ) . split(",")
        # transform to lowercase
        wanted_pokemon = [a.lower() for a in wanted_pokemon]
        # get api key
        api_key = _str( data["pushbullet"] )
        pushbullet_client = Pushbullet(api_key)


# Safely parse incoming strings to unicode
def _str(s):
  return s.encode('utf-8').strip()

# Notify user for discovered Pokemon
def pokemon_found(pokemon):
    # get name
    pokename = _str( pokemon["name"] ).lower()
    # check array
    if not pokename in wanted_pokemon: return
    # notify
    print "[+] Notifier found pokemon:", pokename
    address = Nominatim().reverse(str(pokemon["lat"])+", "+str(pokemon["lng"])).address
    notification_text = "Pokemon Finder found a " + _str(pokemon["name"]) + "!"
    disappear_time = str(datetime.fromtimestamp(pokemon["disappear_time"]).strftime("%I:%M%p").lstrip('0'))+")"
    location_text = "Go search at this location: " + address + ". " + _str(pokemon["name"]) + " will be available until " + disappear_time + "."
    push = pushbullet_client.push_note(notification_text, location_text)



init()
