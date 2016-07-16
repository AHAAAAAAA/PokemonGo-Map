# Pokemon-Map
Live visualization of all the pokemon in your area, building off [Mila432](https://github.com/Mila432/Pokemon_Go_API)'s PokemonGo API, [leegao's additions](https://github.com/leegao/pokemongo-api-demo/tree/simulation) and [Flask-GoogleMaps](https://github.com/rochacbruno/Flask-GoogleMaps). Proof of concept that we can load all the pokemon visible nearby given a location.

Currently really rough, shows duplicate pokemon and requires refreshing page a lot (until the PokemonGo servers decide we're worthy). However, it works.

# Installation
`pip install -r requirements.txt`

# Usage
`python example.py -u myUsername -p myPassword -l "Boulder, CO" -st 20`

-st being steps to take
