#!/usr/bin/env python
from slacker import Slacker
import MySQLdb

slack = Slacker('SLACK-API-TOKEN-GOES-HERE')

#what Pokemon are you wanting to be alerted about?
pokemon_id = 150

db = MySQLdb.connect('localhost', 'USER-GOES-HERE', 'PASSWORD-GOES-HERE', 'DATABASE-GOES-HERE')
cursor = db.cursor()

while TRUE:
    cursor.execute("SELECT pokemon_id, disappear_time from pokemon where pokemon_id = %s and disappear_time >=CURTIME()" % (pokemon_id))

    if cursor.rowcount > 0 :
        slack.chat.post_message('#channel', 'The pokemon you are seeking has been found')
        break
