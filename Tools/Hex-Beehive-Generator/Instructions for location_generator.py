https://github.com/AHAAAAAAA/PokemonGo-Map/wiki/How-to-use-Hex-Beehive-Generator

Location_generator.py creates a list of locations in a hexagonal grid pattern around a central point.

Arguments: -st: steps -lp: leaps (like steps, but for number of workers) -lat: start latitude -lon start longitude

beehive_builder.sh is a bash script that calls location_generator.py with given arguments and creates a script that will run workers at all the generated locations and a server-only process.

Usage: ./beehive_builder.sh "steps" "leaps" "center latitude" "center longitude"


