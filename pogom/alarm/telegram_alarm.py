import logging

from alarm import Alarm, gmaps_link, pkmn_time_text
import telepot

log = logging.getLogger(__name__)

class Telegram_Alarm(Alarm):
	
	def __init__(self, api_key, chatid):
		self.client = telepot.Bot(api_key) 
		self.channel = chatid
		log.info("Telegram_Alarm intialized.")
		self.client.sendMessage(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
		
	def pokemon_alert(self, pokemon):
		notification_text = "A wild " + pokemon['name'].title() + " has appeared!"
		google_maps_link = gmaps_link(pokemon["lat"], pokemon["lng"])
		time_text =  pkmn_time_text(pokemon['disappear_time'])
                self.client.sendMessage(self.channel, '<b>' + notification_text + '</b> \n' + google_maps_link + '\n' + time_text, parse_mode='HTML', disable_web_page_preview='False')
