#!/bin/sh

# If the repo has already been cloned, pull the latest changes
# Otherwise just clone the repo
if [ -d "PokemonGo-Map" ]; then
    cd PokemonGo-Map
    git pull
    pip install -r requirements.txt
    python example.py --port 8090 --host 0.0.0.0 "$@"

else
    git clone https://github.com/AHAAAAAAA/PokemonGo-Map.git
    cd PokemonGo-Map
    pip install -r requirements.txt
    python example.py --port 8090 --host 0.0.0.0 "$@"
fi


