import logging

from alarm import Alarm, gmaps_link, pkmn_time_text
from slacker import Slacker

log = logging.getLogger(__name__)

class Slack_Alarm(Alarm):
	
	def __init__(self, api_key, channel):
		self.client = Slacker(api_key) 
		self.channel = channel
		log.info("Slacker_Alarm intialized.")
		self.client.chat.post_message(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
		
	def pokemon_alert(self, pokemon):
		notification_text = "A wild " + pokemon['name'].title() + " has appeared!"
		google_maps_link = gmaps_link(pokemon["lat"], pokemon["lng"])
		time_text =  pkmn_time_text(pokemon['disappear_time'])
		self.client.chat.post_message(self.channel, notification_text + " " + time_text + " " + google_maps_link)