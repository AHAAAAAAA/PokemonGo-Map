#!/bin/sh

# Fill this variables with your desired options
loc="$1"                             # Location
auth=""                              # PTC or google
user=""                              # User
passwd=""                            # Password
steps=5                              # Number of steps
refresh=3                            # Refresh rate
host="localhost"                     # Host IP
port=5000                            # Host Port
locale="-Len"                        # Locale
ignore="-i Pidgey,Zubat"             # -i to ignore/ -o to only display those pokemons
opts="-dg"                           # Aditional options: -dg/--display-gym, -dp/--display-pokestop , -ol/--onlylure, -d/--debug, -c/--china

if [ \( "$user" = "" \) -o \( "$passwd" = "" \) -o \( "$auth" = "" \) ];then
    echo "Please open this script and configure it first"
    exit 1
elif [ "$#" -eq 0 ];then
    echo "Insert valid location as parameter and nothing more. E.g. 'sh run.sh \"Boulder, CO\"'"
    exit 1
elif [ "$#" -ne 1 ];then
    echo "Pleae insert a valid location between \" \""
	exit 1
elif [ \( "$auth" != "PTC" \) -a \( "$auth" != "google" \) ];then
    echo "Please enter a valid auth method (PTC or google)"
    exit 1
fi

python2 example.py -a "$auth" -u "$user" -p "$passwd" -l "$loc" -st "$steps" -ar "$refresh" -H "$host" -P "$port" "$locale" "$ignore" "$opts"
