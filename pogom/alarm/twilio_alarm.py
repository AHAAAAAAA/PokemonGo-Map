import logging

from alarm import Alarm, gmaps_link, pkmn_time_text
from twilio.rest import TwilioRestClient

log = logging.getLogger(__name__)

class Twilio_Alarm(Alarm):
	
	def __init__(self, account_sid, auth_token, from_num, to_num):
		self.client = TwilioRestClient(account_sid, auth_token) 
		self.from_num = from_num
		self.to_num = to_num
		log.info("Twilio_Alarm intialized.")
		self.send_sms("PokeAlarm has been activated! We will text this number about pokemon.")
		
	def pokemon_alert(self, pokemon):
		notification_text = "A wild " + pokemon['name'].title() + " has appeared!"
		google_maps_link = gmaps_link(pokemon["lat"], pokemon["lng"])
		time_text =  pkmn_time_text(pokemon['disappear_time'])
		self.send_sms(notification_text + " " + time_text + " " + google_maps_link)
		
	def send_sms(self, msg):
		message = self.client.messages.create(body=msg,
			to=self.to_num,    
			from_=self.from_num)