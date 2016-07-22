import json
from pushbullet import Pushbullet
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
        if api_key:
            pushbullet_client = Pushbullet(api_key)


# Safely parse incoming strings to unicode
def _str(s):
  return s.encode('utf-8').strip()

# Notify user for discovered Pokemon
def pokemon_found(pokemon):
    # get name
    pokename = _str(pokemon["name"]).lower()
    # check array
    if not pushbullet_client or not pokename in wanted_pokemon: return
    # notify
    print "[+] Notifier found pokemon:", pokename

    #http://maps.google.com/maps/place/<place_lat>,<place_long>/@<map_center_lat>,<map_center_long>,<zoom_level>z
    latLon = '{},{}'.format(repr(pokemon["lat"]), repr(pokemon["lng"]))
    google_maps_link = 'http://maps.google.com/maps/place/{}/@{},{}z'.format(latLon, latLon, 20)

    notification_text = "Pokemon Finder found " + _str(pokemon["name"]) + "!"
    disappear_time = str(datetime.fromtimestamp(pokemon["disappear_time"]).strftime("%I:%M%p").lstrip('0'))+")"
    location_text = "Locate on Google Maps : " + google_maps_link + ". " + _str(pokemon["name"]) + " will be available until " + disappear_time + "."

    push = pushbullet_client.push_link(notification_text, google_maps_link, body=location_text)



init()
