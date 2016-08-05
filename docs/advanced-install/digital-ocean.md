# DigitalOcean

**Note:** There have been reports of Niantic servers blocking requests from DigitalOcean's major IP blocks (as well as Amazon AWS, and Microsoft Azure): login failures with the Error 403 are due to this. If you are experiencing this issue there is nothing we can do about it at this time.

## Prerequisites

- [A DigitalOcean account](https://m.do.co/c/fb6730f5bb99) - Using this link will grant $10 in credit, enough for running your server for up to 2 months.
- [A Google Maps API key](GoogleMaps.md)
- [A new Pokemon Club account](https://club.pokemon.com/us/pokemon-trainer-club/sign-up/)

## Installation

Create a Droplet in your DigitalOcean control panel with Ubuntu 16.04, any Droplet size will work.

Check the "User Data" box lower on the page and enter the following:

```
#!/bin/bash

apt-get -y update
apt-get -y install python python-pip git
git clone https://github.com/AHAAAAAAA/PokemonGo-Map.git /root/PoGoMap
cd /root/PoGoMap
pip install -r requirements.txt
python runserver.py -u [USERNAME] -p [PASSWORD] -st 10 -k [Google Maps API key] -l "[LOCATION]" -H 0.0.0.0 -P 80
```

**Important:** Be sure to replace `[USERNAME]`, `[PASSWORD]`, [API Key]`, and `[LOCATION]` with your Pokemon Trainers Club Username and Password, your Google Maps API Key, and your location (Latitude and Longitude), respectively. You will be able to change locations later on the site.

Once you have that, create your Droplet. Setup will take a few minutes initially, but once it's done your map will be accessible at `http://[YOURDROPLET]/`, replacing that of course with your Droplet's IP address.

## Starting the server

On the first boot the server will start automatically so this step isn't necessary, however if you have to restart the Droplet for any reason, you can start PoGoMap with the following two commands:

```
cd /root/PoGoMap
python runserver.py -u [USERNAME] -p [PASSWORD] -st 10 -k [Google Maps API key] -l "[LOCATION]" -H 0.0.0.0 -P 80
```

Credit: [JonahAragon](https://github.com/JonahAragon)
