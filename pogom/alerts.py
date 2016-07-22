#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import time
import datetime
import smtplib
from . import config
from .models import Pokemon
from pogom.utils import load_pokemon_alerts
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)

pokemon_ids = load_pokemon_alerts(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

def find_alertable_pokemon():
	active_pokemon = Pokemon.get_active()
	for pokemon in active_pokemon:
		if not pokemon['alerted'] and pokemon['pokemon_id'] in pokemon_ids:
			send_email(pokemon)
			Pokemon.mark_alerted(pokemon['encounter_id'])

def send_email(pokemon):
	if pokemon['pokemon_name'] == u'Nidoran\u2642':
		pokemon['pokemon_name'] = 'Nidoran-M'
	elif pokemon['pokemon_name'] == u'Nidoran\u2640':
		pokemon['pokemon_name'] = 'Nidoran-F'

	email_address = config['GMAIL_USERNAME']
	password = config['GMAIL_PASSWORD']

	msg= MIMEMultipart('alternative')
	msg['Subject'] = "A " + pokemon['pokemon_name'] + " was spotted near you!"
	msg['From'] = email_address
	msg['To'] = email_address
	
	text_body = get_text_body(pokemon)
	html_body = get_html_body(pokemon)
	log.info(text_body)
	mime_text = MIMEText(text_body, 'plain')
	mime_html = MIMEText(html_body, 'html')
	msg.attach(mime_text)
	msg.attach(mime_html)

	try:
		smtp = smtplib.SMTP('smtp.gmail.com', 587)
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
		smtp.login(email_address, password)
		smtp.sendmail(email_address, email_address, msg.as_string())
		smtp.quit()
	except smtplib.SMTPException:
		print "Unable to send mail."

def get_disappears_at_units(pokemon):
	time_delta = pokemon['disappear_time'] - datetime.datetime.utcnow()
	hours = time_delta.seconds / 3600
	minutes = (time_delta.seconds % 3600) / 60
	seconds = time_delta.seconds % 60
	return (hours, minutes, seconds)

def get_html_body(pokemon):
	hours, minutes, seconds = get_disappears_at_units(pokemon)
	map_link = "https://www.google.com/maps?q=%f,%f" % (pokemon['latitude'], pokemon['longitude'])
	html = """
		<html>
			<head></head>
			<body>"""
	html += "<p>Newly spawned Pokemon found: <strong>" + pokemon['pokemon_name'] + "</strong></p>"
	html += "<p>It will disappear in %s hours %s minutes %s seconds.</p>" % (str(hours), str(minutes), str(seconds))
	html += "<p><a href='%s' target='_blank'>Map</a></p>" % (map_link)
	html += """
			</body>
				</html>"""
	return html


def get_text_body(pokemon):
	hours, minutes, seconds = get_disappears_at_units(pokemon)
	return "Newly spawned Pokemon found: " + pokemon['pokemon_name'] + ". It will disappear in " + str(hours) + " hours " + str(minutes) + " minutes " + str(seconds) + " seconds."

def alerting_loop(args):
	while True:
		find_alertable_pokemon()
		time.sleep(5)
