# Pokemon Go Notification System

This is a fork of [the popular PokemonGo-Map repository](https://github.com/AHAAAAAAA/PokemonGo-Map) with the purpose of allowing users to search for specific Pokemon without having to constantly monitor the map of nearby Pokemon. This allows users to set a list of sought-after Pokemon and receive notifications through [Pushbullet](https://www.pushbullet.com/). All API and map functionality was left untouched.

## Configure PushBullet
To generate a token for sending yourself notifications using the Pushbullet API, create an account on [Pushbullet](https://www.pushbullet.com/). Then click your avatar and select the "My Account" page. Scroll to where you see "Access Tokens" and click the "Create Access Token" button. Copy this hash, you'll need it later.

## Config File
Instead of from the command-line, all arguments are read from a `config.json` file. In addition to all of the options laid out [here](https://github.com/AHAAAAAAA/PokemonGo-Map/wiki/Usage), I've introduced two required fields: `pushbullet`, your Pushbullet API key, and `notify`, a comma-separated list of the Pokemon that you'd like to receive Pushbullet notifications for.
As an alernative to 'notify', you may also make use of a field called 'do_not_notify'. If the 'do_not_notify' field is present and the 'notify' field is not present, you will be notified for ALL pokemon except the ones in the 'do_not_notify' field.

Here's a sample `config.json` using the 'notify' field:

```
{
  "auth_service": "google",
  "username": "myemailuser",
  "password": "pikachu123",
  "step_limit": 5,
  "location": "742 Evergreen Terrace, Arlington, VA",
  "notify": "dratini,magnemite,electabuzz,hitmonchan,hitmonlee,chansey,lapras,snorlax,porygon,mew,mewtwo,moltres,zapdos,articuno,ditto,seel,gyarados,cubone",
  "pushbullet": "o.XyDeiVeYuM5eSv2ssy7AlFGLDl4ajEXj"
}
```

Here's a sample `config.json` using the 'do_not_notify' field:

```
{
  "auth_service": "google",
  "username": "myemailuser",
  "password": "pikachu123",
  "step_limit": 5,
  "location": "742 Evergreen Terrace, Arlington, VA",
  "do_not_notify": "rattata,raticate,pidgey,pidgeotto,venonat,zubat,golbat,magikarp,weedle,kakuna,caterpie,metapod",
  "pushbullet": "o.XyDeiVeYuM5eSv2ssy7AlFGLDl4ajEXj"
}
```

## Install

Install the necessary dependencies (including the Pushbullet client) by running `pip install --upgrade -r requirements.txt`. Create a config file and then run the main script using `python main.py`.

*Using this software is against the ToS and can get you banned. Use at your own risk.*

## Notifications
You'll have to set up notifications where you'd like to receive them. I installed the [Pushbullet Chrome Extension](https://chrome.google.com/webstore/detail/pushbullet/chlffgpmiacpedhhbkiomidkjlcfhogd?hl=en) and then decided that I found more utility by installing the Pushbullet iPhone app and receiving the notifications on my phone.

## Screenshots

<p align="center">
  <img src="https://raw.githubusercontent.com/jxmorris12/PokemonGo-Finder/master/screenshots/PhonePushNotif.PNG" height="500">
  <img src="https://raw.githubusercontent.com/jxmorris12/PokemonGo-Finder/master/screenshots/ChromePushNotif.png" width="400">
  <img src="https://raw.githubusercontent.com/AHAAAAAAA/PokemonGo-Map/master/static/cover.png">
</p>
