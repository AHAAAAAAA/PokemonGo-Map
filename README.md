# PokemonGo Map Web Client

Live visualization of all the pokemon (with option to show gyms and pokestops) in your area. This is a proof of concept that we can load all the pokemon visible nearby given a location. Currently runs on a Flask server displaying a Google Maps with markers on it.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://github.com/AHAAAAAAA/PokemonGo-Map-server/wiki/Heroku-Deployment)

#[Official Twitter] (https://twitter.com/PoGoMDev) Please give us a follow or contact.
#[Official Website] (https://jz6.github.io/PoGoMap/)#

![Map](https://raw.githubusercontent.com/AHAAAAAAA/PokemonGo-Map-server/master/static/cover.png)

## How to setup

You will need:

1. A Pokemon Trainer Club account: <https://club.pokemon.com/us/pokemon-trainer-club/sign-up/>
2. Google Maps API Key: <https://developers.google.com/maps/documentation/javascript/get-api-key>
3. Current versions of [`node`](https://nodejs.org), `grunt`, `ruby`, and `gem`.

```bash
gem install sass
npm install --global grunt

git clone https://github.com/AHAAAAAAA/PokemonGo-Map-web-client
cd PokemonGo-Map-web-client

npm install
```

The **Google Maps API Key** should be changed in `static/js/config.js`:

```html
// CHANGE ME
var CONFIG = {
  latitude: 40.36915523640919
, longitude: -111.75098587678943
, gmaps_key: 'AIzaSyAZzeHhs-8JZ7i18MjFuM35dJHq70n3Hx4'
}
```

The key above **WILL NOT WORK**, it is just an example.
You **MUST** [get your own key](https://developers.google.com/maps/documentation/javascript/get-api-key)
(but it only takes 60 seconds or so).

This client works in conjunction with the original `PokemonGo Map` (python), `node-pokemap` (node.js),
or any server that correctly implements the APIs (mentioned below).

For instructions on how to setup and run the server, please refer to the server project you prefer:

* [PokemonGo-Map-server](https://github.com/AHAAAAAAA/PokemonGo-Map-server)
* [node-pokemap](https://github.com/Daplie/node-pokemap)

## API Endpoints

* `POST /login` - change the current logged in user
* `GET /raw_data` - returns a json object representing the list of nearby pokemon, pokestops, and gyms
* `GET /loc` - return the current gps location
* `POST /next_loc` - update the gps location
* `GET /pokemon` - get list of active pokemon

## Warnings

Using this software is against the ToS of the game. You can get banned, use this tool at your own risk.


## Contributing

Please submit all pull requests to [develop](https://github.com/AHAAAAAAA/PokemonGo-Map-web-client/tree/develop) branch.

Building off [Mila432](https://github.com/Mila432/Pokemon_Go_API)'s PokemonGo API, [tejado's additions](https://github.com/tejado/pokemongo-api-demo), [leegao's additions](https://github.com/leegao/pokemongo-api-demo/tree/simulation) and [Flask-GoogleMaps](https://github.com/rochacbruno/Flask-GoogleMaps).
