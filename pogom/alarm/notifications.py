import os
import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)

from pb_alarm import PB_Alarm
from slack_alarm import Slack_Alarm
from twilio_alarm import Twilio_Alarm
from ..utils import get_pokemon_name

class Notifications:

	def __init__(self):
		filepath = os.path.dirname(os.path.dirname(__file__))
		with open(os.path.join(filepath, '..', 'alarms.json')) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = settings["pokemon"]
			self.seen = {}
			self.alarms = []
			for alarm in alarm_settings:
				if alarm['active'] == "True" :
					if alarm['type'] == 'pushbullet' :
						self.alarms.append(PB_Alarm(alarm['api_key']))
					if alarm['type'] == 'slack' :
						self.alarms.append(Slack_Alarm(alarm['api_key'], alarm['channel']))
					if alarm['type'] == 'twilio' :
						self.alarms.append(Twilio_Alarm(alarm['account_sid'], alarm['auth_token'], alarm['to_number'], alarm['from_number']))
				else:
					log.info("Invalid alarm type specified: " + alarm['type'])
			
				
	def notify_pkmns(self, pkmn):
		for id in pkmn:
			if id not in self.seen:
				pkinfo = {
					'name': get_pokemon_name(pkmn[id]['pokemon_id']),
					'lat': pkmn[id]['latitude'],
					'lng': pkmn[id]['longitude'],
					'disappear_time': pkmn[id]['disappear_time']
				}
				self.seen[id] = pkinfo
				if(self.notify_list[pkinfo['name']] == "True"):
					log.info(pkinfo['name']+" notification has been triggered!")
					for alarm in self.alarms:
						alarm.pokemon_alert(pkinfo)
		self.clear_stale()

	#clear stale so that the seen set doesn't get too large
	def clear_stale(self):
		old = []
		for id in self.seen:
			if self.seen[id]['disappear_time'] < datetime.utcnow() :
				old.append(id)
		for id in old:
			del self.seen[id]

	def notify_lures(self, lures):
		raise NotImplementedError("This method is not yet implimented.")
		
	def notify_gyms(self, gyms):
		raise NotImplementedError("This method is not yet implimented.")
	