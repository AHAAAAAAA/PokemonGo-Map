# OSX Install

In order to run the project, you will need Python, pip and the project dependencies.
Version 2.7 is what we usually test against. You can use 3.x but no support will be given.

## Prerequisites for this guide

 - Mac OSX 10.9+
 - [Homebrew for Mac](http://brew.sh/)

## Step 1: Install Homebrew

**Open up Terminal**

1. Click on the rocket ship
2. In the search, type in `Terminal`
3. Type:

   ```
   /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
   ```

## Step 2: Install Requirements

```
brew install git python python protobuf
```

## Step 3: Clone PokemonGo-Map

For this guide we'll be using the Documents folder.

**While still in the Terminal**

1. Navigate to the user home folder.

   ```
   cd ~/Documents`
   ```

2. Clone the repository

   ```
   git clone https://github.com/AHAAAAAAA/PokemonGo-Map.git
   ```

Now we have all PokemonGo-Map files inside our Documents folder. Git clone automatically creates a folder called PokemonGo-Map

## Step 4: Get your own Google Maps API Key

Read up on [the maps key page]()
Go to [this page](https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend,places_backend&keyType=CLIENT_SIDE&reusekey=true) to get your own Google Maps API Key. If you do not get your own API Key, you'll very likely run into an error telling you that you reached the daily request limit. **Additionally, you do not need to just get the key but you need to ensure the Google Maps JavaScript API is enabled for your account.** This is done from the homepage of the Google developer tools. Just getting the key alone does not automatically enable the JavaScript API that is necessary for the application.

If you got your own API Key, open the *credentials.json* file inside the *PokemonGo-Map/config* folder. You can edit that file with Mac's built in text editor. Now replace the API Key in line 6 with the one you got from that Google website.

## Step 6: Setup PokemonGo-Map

**While still in the Terminal:**

1. Navigate into PokemonGo-Map folder

   ```
   cd ~/Documents/PokemonGo-Map
   ```

2. Install specific python requirements

   ```
   pip install --upgrade -r requirements.txt
   ```

## Step 7: Start PokemonGo-Map

Now we are ready to start the map.

A full list of parameters you can use with the map and what they mean can be found [here](https://github.com/AHAAAAAAA/PokemonGo-Map#usage). This guide will only cover the important ones:

-a: Use either `ptc` or `google` for the login
-u: Your Username
-p: Your Password
-l: The location you want to scan for Pokémon. You can try something like `La tour Eiffel, Paris`, your street or exact coordinates in this format: `47.6062100 -122.3320700`
-st: The amount of steps to take (5 steps is approximately a 1.2km radius according to [this list](https://github.com/AHAAAAAAA/PokemonGo-Map#usage))

> **Note**: It's recommended that you create a dummy account to use this Map with in order to prevent your real account from getting (soft)banned.

The final command should look like this (for master branch):

```
python runserver.py -a ptc -u johndoe -p ilovemama -l "400 Broad St, Seattle, WA 98109, USA" -st 5
```

If you are working in the develop branch, then use runserver.py instead of example.py

Hit enter and view your map in all it's glory at http://127.0.0.1:5000/. Done!

![Map](../_static/img/EBkRhvZ.png)

## Bonus: How to update PokemonGo-Map

Since PokemonGo-Map is under active development and gets a lot of updates, you probably want to get all the latest features and bug fixes. You can see the latest updates (called commits) [here](https://github.com/AHAAAAAAA/PokemonGo-Map/commits/master). To update your copy, *Git Bash here* from the PokemonGo-Map folder, paste this command and hit enter:

```
git pull
```

Now repeat Step 7 to restart your map.