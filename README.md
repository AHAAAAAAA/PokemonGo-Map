# PokemonGo Map Server

Live visualization of all the pokemon (with option to show gyms and pokestops) in your area. This is a proof of concept that we can load all the pokemon visible nearby given a location. Currently runs on a Flask server displaying a Google Maps with markers on it.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://github.com/AHAAAAAAA/PokemonGo-Map-server/wiki/Heroku-Deployment)

#[Official Twitter] (https://twitter.com/PoGoMDev) Please give us a follow or contact.
#[Official Website] (https://jz6.github.io/PoGoMap/)#

![Map](https://raw.githubusercontent.com/AHAAAAAAA/PokemonGo-Map/master/static/cover.png)


## How to setup

```bash
git clone https://github.com/AHAAAAAAA/PokemonGo-Map-server
cd PokemonGo-Map-server/

git clone https://github.com/AHAAAAAAA/PokemonGo-Map-web-client
ln -s PokemonGo-Map-web-client/static/ ./

pip install -r requirements.txt

python runserver.py -u $USERNAME -p $PASSWORD -st 10 -l "$LOCATION" --host 127.0.0.1
```

If you want to login with Google instead of Pokemon Trainer Club add `-a google`:

```
python runserver.py -a google -u $USERNAME -p $PASSWORD -st 10 -l "$LOCATION" --host 127.0.0.1
```

You can now access the server at <http://localhost:5000>.

For more advanced instructions on how to setup and run the tool, please refer to the project [wiki](https://github.com/AHAAAAAAA/PokemonGo-Map-server/wiki), or the [video guide](https://www.youtube.com/watch?v=RJKAulPCkRI).

## API Endpoints

* `POST /login` - change the current logged in user
* `GET /raw_data` - returns a json object representing the list of nearby pokemon, pokestops, and gyms
* `GET /loc` - return the current gps location
* `POST /next_loc` - update the gps location
* `GET /pokemon` - get list of active pokemon

## Android Version

There is an [Android port](https://github.com/omkarmoghe/Pokemap) in the works. All Android related prs and issues please refer to this [repo](https://github.com/omkarmoghe/Pokemap).


## Warnings

Using this software is against the ToS of the game. You can get banned, use this tool at your own risk.


## Contributing

Please submit all pull requests to [develop](https://github.com/AHAAAAAAA/PokemonGo-Map/tree/develop) branch.

Building off [Mila432](https://github.com/Mila432/Pokemon_Go_API)'s PokemonGo API, [tejado's additions](https://github.com/tejado/pokemongo-api-demo), [leegao's additions](https://github.com/leegao/pokemongo-api-demo/tree/simulation) and [Flask-GoogleMaps](https://github.com/rochacbruno/Flask-GoogleMaps).
