#!/usr/bin/python
# -*- coding: utf-8 -*-

# This py works as email trigger, which will send you email with
# a google map link with directions on how to get there

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .utils import get_pokemon_name

log = logging.getLogger(__name__)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
# Fill this. e.g. server.login("your_gmail_username", "your_gmail_password")
server.login("", "")

# Where to send email and who is the sender
# It can be the same email. e.g. your_gmail_username@gmail.com
email_source = ""
email_destination = ""

# Pokemon ID's which will trigger the email
# For example if you want to receive email about Blastoise
# and Charizard do this:
# EMAIL_TRIGGER_IDS = [9, 6]
EMAIL_TRIGGER_IDS = []

def send_email(pokemon_id, latitude, longitude):
    if pokemon_id in EMAIL_TRIGGER_IDS:
        pokename = get_pokemon_name(pokemon_id)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Wanted pokemon alert"
        msg['From'] = email_source
        msg['To'] = email_destination

        text = "%s appeared near you." % (pokename)
        html = """\
        <html>
          <head></head>
          <body>
            <p>
                %s appeared near you.<br>
                Directions:
                <a href='https://www.google.com/maps/dir/Current+Location/ %s, %s' target='_blank' title='View in Maps'>
                    Google maps
                </a>
            </p>
          </body>
        </html>
        """ % (pokename, str(latitude), str(longitude))

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        log.info('Sending email about {:s}'.format(pokename))
        server.sendmail(email_source, email_destination, msg.as_string())
