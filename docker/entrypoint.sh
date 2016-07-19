#!/bin/sh

if [ -d "PokemonGo-Map" ]; then
    cd PokemonGo-Map
    git pull
    pip install -r requirements.txt
    python example.py --port 8090 --host 0.0.0.0 "$@"
  # Control will enter here if $DIRECTORY exists.
else
    git clone https://github.com/AHAAAAAAA/PokemonGo-Map.git
    cd PokemonGo-Map
    pip install -r requirements.txt
    python example.py --port 8090 --host 0.0.0.0 "$@"
fi


