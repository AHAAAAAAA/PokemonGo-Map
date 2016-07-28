from datetime import datetime
from slacker import Slacker

def slackAlert(doc, pokemon_name, pokemon_rarity, pokemon_id, lat, lng, itime):
    slack_channel = doc['slack']['channel']
    api_key = doc['slack']['api_key']
    username = 'PokemonGo Alerts'
    icon_url = 'https://upload.wikimedia.org/wikipedia/en/3/39/Pokeball.PNG'
    timeLeft = itime-datetime.utcnow()
    mapLink = "https://www.google.com/maps/dir/Current+Location/%s,%s" % (lat,lng)
    attachment = [
        {
            "color": "warning",
            "pretext": ":eyes: %s Spotted" % (pokemon_name.encode('utf-8')),
            "title": "Information:",
            "text": "Name: %s \n Rarity: %s\n ID: %s \n Remaining Time: %s \n Directions: %s" % (
                pokemon_name.encode('utf-8'), pokemon_rarity.encode('utf-8'),
                pokemon_id, str(timeLeft), mapLink
            ),
            "mrkdwn_in": [
                "text",
                "pretext"
            ]
        }
    ]
    if api_key:
        slack = Slacker(api_key)
    else:
        print "ERROR: No Slack API Key supplied"
    if slack_channel:
        if not slack_channel.startswith('#'):
            slack_channel = '#' + slack_channel
        slack.chat.post_message(slack_channel, '', username=username, icon_url=icon_url, attachments=attachment)
    else:
        print "ERROR: No Slack channel supplied"
