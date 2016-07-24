import json
from pushbullet import Pushbullet
from datetime import datetime
import sys

# Fixes the encoding of the male/female symbol
reload(sys)
sys.setdefaultencoding('utf8')

pushbullet_client = None
wanted_pokemon = None
unwanted_pokemon = None

# Initialize object
def init():
    global pushbullet_client, wanted_pokemon, unwanted_pokemon
    # load pushbullet key
    with open('config.json') as data_file:
        data = json.load(data_file)
        # get list of pokemon to send notifications for
        if "notify" in data:
            wanted_pokemon = _str( data["notify"] ) . split(",")

            # transform to lowercase
            wanted_pokemon = [a.lower() for a in wanted_pokemon]
        #get list of pokemon to NOT send notifications for
        if "do_not_notify" in data:
            unwanted_pokemon = _str( data["do_not_notify"] ) . split(",")

            # transform to lowercase
            unwanted_pokemon = [a.lower() for a in unwanted_pokemon]
        # get api key
        api_key = _str( data["pushbullet"] )
        if api_key:
            pushbullet_client = Pushbullet(api_key)


# Safely parse incoming strings to unicode
def _str(s):
  return s.encode('utf-8').strip()

  

  
  
# Notify user for discovered Pokemon
def pokemon_found(pokemon):
    #pushbulley channel 
    # Or retrieve a channel by its channel_tag. Note that an InvalidKeyError is raised if the channel_tag does not exist
    my_channel = pushbullet_client.get_channel('CHANNELNAME HERE')  
    # get name
    pokename = _str(pokemon["name"]).lower()
    # check array
    if not pushbullet_client:
        return
    elif wanted_pokemon != None and not pokename in wanted_pokemon:
        return
    elif wanted_pokemon == None and unwanted_pokemon != None and pokename in unwanted_pokemon:
        return
    # notify
    print "[+] Notifier found pokemon:", pokename

    #http://maps.google.com/maps/place/<place_lat>,<place_long>/@<map_center_lat>,<map_center_long>,<zoom_level>z
    latLon = '{},{}'.format(repr(pokemon["lat"]), repr(pokemon["lng"]))
    google_maps_link = 'http://maps.google.com/maps/place/{}/@{},{}z'.format(latLon, latLon, 20)

    notification_text = "Pokemon Found " + _str(pokemon["name"]) + "!"
    disappear_time = str(datetime.fromtimestamp(pokemon["disappear_time"]).strftime("%I:%M%p").lstrip('0'))+")"
    location_text = "Location : " + google_maps_link + ". " + _str(pokemon["name"]) + " Available till " + disappear_time + "."
    push = pushbullet_client.push_link(notification_text, google_maps_link, body=location_text, channel=my_channel)
    #push = pushbullet_client.push_link(notification_text, google_maps_link, body=location_text)



init()
