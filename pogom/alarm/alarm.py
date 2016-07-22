import logging
import json

from datetime import datetime
from ..utils import get_pokemon_name

log = logging.getLogger(__name__)

class Alarm(object):
	
	def __init__(self, list):
		#set of pokemon to care about
		self.pkmn_list = list
		
		#pokemon that have already been proccessed
		self.seen = {}
		
	def notify_pokemon(self, pkmn):
		for id in pkmn:
			if id not in self.seen:
				pkinfo = {
					'name': get_pokemon_name(pkmn[id]['pokemon_id']).lower(),
					'lat': pkmn[id]['latitude'],
					'lng': pkmn[id]['longitude'],
					'time': (pkmn[id]['disappear_time'] - datetime.utcnow())
				}
				self.seen[id] = pkinfo
				if(self.pkmn_list[pkinfo['name']] == "True"):
					self.pokemon_alert(pkinfo)
					log.info(pkinfo['name']+" notification has been triggered!")
				
	def pokemon_alert(self, pokemon):
		raise NotImplementedError("Please Implement this method")
		