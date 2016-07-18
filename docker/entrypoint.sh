#!/bin/sh

wget https://github.com/AHAAAAAAA/PokemonGo-Map/archive/master.zip
unzip master.zip
rm master.zip
cd PokemonGo-Map-master
pip install -r requirements.txt
python example.py --port 8090 "$@"


