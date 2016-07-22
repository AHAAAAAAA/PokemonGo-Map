
import logging
from datetime import datetime

from alarm import Alarm
from pushbullet import PushBullet

log = logging.getLogger(__name__)

class PB_Alarm(Alarm):
	
	def __init__(self, api_key, list):
		Alarm.__init__(self, list)
		self.client = PushBullet(api_key) 
		log.info("PB_Alarm intialized.")
		push = self.client.push_link("PokeAlarm activated!", "Link here", body="We will alert you about pokemon")
		
	def pokemon_alert(self, pokemon):
		google_maps_link = "https://www.google.com/maps?q=" + str(pokemon["lat"]) + "," + str(pokemon["lng"])
		notification_text = "Pokemon found: " + pokemon['name'].title()
		s = pokemon["time"].total_seconds()
		(m, s) = divmod(s, 60)
		(h, m) = divmod(m, 60)
		body_text = "Available for %dm %ds " % (m, s)
		push = self.client.push_link(notification_text, google_maps_link, body=body_text)
	