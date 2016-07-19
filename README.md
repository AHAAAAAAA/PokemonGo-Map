<p align="center">
<img src="https://cloud.githubusercontent.com/assets/7145349/16916971/6bd3343a-4cb4-11e6-86cc-e3bc9399a9b0.png">
</p>

# PokemonGo Map

[![Build Status](https://travis-ci.org/AHAAAAAAA/PokemonGo-Map.svg?branch=master)](https://travis-ci.org/AHAAAAAAA/PokemonGo-Map)  [![Coverage Status](https://coveralls.io/repos/github/AHAAAAAAA/PokemonGo-Map/badge.svg?branch=master)](https://coveralls.io/github/AHAAAAAAA/PokemonGo-Map?branch=master)

Live visualization of all the pokemon (with option to show gyms and pokestops) in your area. This is a proof of concept that we can load all the pokemon visible nearby given a location. Currently runs on a Flask server displaying a Google Maps with markers on it.

Building off [Mila432](https://github.com/Mila432/Pokemon_Go_API)'s PokemonGo API, [tejado's additions](https://github.com/tejado/pokemongo-api-demo), [leegao's additions](https://github.com/leegao/pokemongo-api-demo/tree/simulation) and [Flask-GoogleMaps](https://github.com/rochacbruno/Flask-GoogleMaps).

---

# Requirements
* Python 2.7.x

# Installation
`pip install -r requirements.txt`

# Usage
`python example.py -a authService -u myUsername -p myPassword -l "Boulder, CO" -st 5`

| Flag                       | Description                                     | Required |
|----------------------------|-------------------------------------------------|----------|
| `-a` `--auth-service`      | Auth service (PTC or google)                    |          |
| `-u` `--username`          | Username                                        | ✓        |
| `-p` `--password`          | Password                                        | ✓        |
| `-l` `--location`          | Any location Google Maps can understand         | ✓        |
| `-st` `--step-limit`       | Steps to take                                   | ✓        |
| `-i` `--ignore`            | Comma-separated list of Pokémon names to ignore |          |
| `-o` `--only`              | Comma-separated list of Pokémon names to search |          |
| `-ar` `--auto-refresh`     | Number of seconds on which to autorefresh       |          |
| `-dp` `--display-pokestop` | Display pokéstops                               |          |
| `-dg` `--display-gym`      | Display gyms                                    |          |
| `-H` `--host`              | Set web server listening host                   |          |
| `-P` `--port`              | Set web server listening port                   |          |
| `-L` `--locale`            | Locale for Pokemon names: default en, check locale folder for more options |          |
| `-c` `--china`             | Coordinates transformer for China               |          |
| `-d` `--debug`             | Debug mode                                      |          |
| `-ol` `--onlylure`         | Display only lured pokéstop                    |          |

_Note:
5 steps is approximately a 1.2km radius. More than 10 is redundant (you usually can't walk that far before despawn anyway)_

## Common Errors
> _`Exception, e <- Invalid syntax.`_

* You are using python 3, download python 2.7 instead.

> _`pip or python is not recognized as an internal or external command`_

* Replace pip with C:\Python27\Scripts\pip
* Replace python with C:\Python27\python

## FAQ
> _Can I sign in with Google?_

* Yes you can! Pass the flag `-a google` to use Google authentication

> _I'm on Windows, why does nothing work?_

* See if anything in https://www.reddit.com/r/pokemongodev/comments/4t80df/wip_pokemon_go_map_visualization_google_maps_view/d5feu2f helps
