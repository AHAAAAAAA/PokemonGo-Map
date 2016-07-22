import os
import json

from pb_alarm import PB_Alarm

def create_alarm(filepath):
	with open(filepath+os.path.sep+'credidentials.alarm.json') as file:
		creds = json.load(file)
		pkmn = json.load(open(filepath+os.path.sep+'pokemon.alarm.json'))
		if creds['type'] == 'pushbullet':
			return PB_Alarm(creds['api_key'], pkmn)
		else:
			return None 