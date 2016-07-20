#!/bin/bash


change_api_keys () 
{
# Change the API keys in credentials.json 
# If a variable with the value is provided
    for VAR in `env`
    do
      case "$VAR" in
          POKEMON_* )
        key_name=`echo "$VAR" | sed -e "s/^POKEMON_\(.*\)\=.*/\1/"`
        echo "Changing value of " $key_name
        key_value=`echo "$VAR" | sed -e "s/.*=\(.*\)/\1/"`
        cat credentials.json |
            jq "to_entries |
                 map(if .key == \"$key_name\"
                    then . + {\"value\":\"$key_value\"}
                    else .
                    end
                   ) |
                from_entries" > modified_credentials.json
        mv modified_credentials.json credentials.json
        ;;
        esac
    done
}

# If the repo has already been cloned, pull the latest changes
# Otherwise just clone the repo
if [ -d "PokemonGo-Map" ]; then
    cd PokemonGo-Map
    git pull
    pip install -r requirements.txt
    change_api_keys
    python example.py --host 0.0.0.0 "$@"

else
    git clone https://github.com/AHAAAAAAA/PokemonGo-Map.git
    cd PokemonGo-Map
    pip install -r requirements.txt
    change_api_keys
    python example.py --host 0.0.0.0 "$@"
fi


