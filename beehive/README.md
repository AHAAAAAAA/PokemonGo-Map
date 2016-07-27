Beehive Usage

==How to generate a script to automatically run a ton of workers==

beehive_builder.sh takes four arguments: steps, leaps, latitude, longitude

steps: same as runserver.py

leaps: like steps, but it defines a radius in terms of workers instead of scans (eg leaps = 1 makes 7 workers)

latitude: the latitude of the central point of the hive

longitude: the longitude of the central point of the hive

Unlike runserver.py, the arguments are not flagged. Instead, they go in a set order. For example, 2 steps, 4 leaps at location "38, -86" would be:

./beehive_builder.sh 2 4 38 -86

==How to run all those workers at once now that we've built a hive==

Run these commands to start the hive.

cd ..
./beehive.sh

==That's nice and all, but I've got my own way of making workers. I just need good locations.==

location_generator.py takes flags -st for steps, -lp for leaps, -lat for latitude, -lon for longitude. It outputs a list of locations to the file locations.txt. Each line of the file is a valid Google Maps location.