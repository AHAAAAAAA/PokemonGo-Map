<<<<<<< HEAD
# PokemonGo Map![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)


Live visualization of all the pokemon (with option to show gyms and pokestops) in your area. This is a proof of concept that we can load all the pokemon visible nearby given a location. Currently runs on a Flask server displaying Google Maps with markers on it.

Features: 
now 

* Shows Pokemon, Pokestops, and gyms with a clean GUI.
* Notifications 
* Lure information
* Multithreaded mode
* Filters
* Independent worker threads (many can be used simulatenously to quickly generate a livemap of a huge geographical area)
* Localization (en, fr, pt_br, de, ru, zh_cn, zh_hk)
* DB storage (sqlite or mysql) of all found pokemon
* Incredibly fast, efficient searching algorithm (compared to everything else available)

[![Deploy](https://raw.githubusercontent.com/sych74/PokemonGo-Map-in-Cloud/master/images/deploy-to-jelastic.png)](https://jelastic.com/install-application/?manifest=https://raw.githubusercontent.com/sych74/PokemonGo-Map-in-Cloud/master/manifest.jps) [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://github.com/AHAAAAAAA/PokemonGo-Map/wiki/Heroku-Deployment) 

#[Twitter] (https://twitter.com/PokemapDev), [Website] (https://jz6.github.io/PoGoMap/)#

![Map](https://raw.githubusercontent.com/AHAAAAAAA/PokemonGo-Map/master/static/cover.png)


## How to setup

For instructions on how to setup and run the tool, please refer to the project [wiki](https://github.com/AHAAAAAAA/PokemonGo-Map/wiki), or the [video guide](https://www.youtube.com/watch?v=RJKAulPCkRI).


## Android Version

There is an [Android port](https://github.com/omkarmoghe/Pokemap) in the works. All Android related prs and issues please refer to this [repo](https://github.com/omkarmoghe/Pokemap).

## iOS Version

There is an [iOS port](https://github.com/istornz/iPokeGo) in the works. All iOS related prs and issues please refer to this [repo](https://github.com/istornz/iPokeGo).

## Warnings

Using this software is against the ToS of the game. You can get banned, use this tool at your own risk.


## Contributions

Please submit all pull requests to [develop](https://github.com/AHAAAAAAA/PokemonGo-Map/tree/develop) branch.

Building off [tejado's python pgoapi](https://github.com/tejado/pgoapi), [Mila432](https://github.com/Mila432/Pokemon_Go_API)'s API, [leegao's additions](https://github.com/leegao/pokemongo-api-demo/tree/simulation) and [Flask-GoogleMaps](https://github.com/rochacbruno/Flask-GoogleMaps). Current version relies primarily on the pgoapi and Google Maps JS API.
=======
# PokemonGo-Map

We've received a notice to cease and desist from Niantic Labs, and I've decided to comply with their requests. It was my intention to augment and improve the game experience of Pokemon Go, and we achieved just that! Without their blessing, I don't see myself having the motivation to continue this project.

It grew from a 2 hour weekend project to a robust 2-click server ready-for-deployment in a matter of days. The project has inspired \~5 million views (500k uniques), 44k clones, 9.6k stars, 160 contributors, translation into 10 languages, and a wonderful community all in the span of 2 weeks. It's also been featured on The Verge, Arstechnica, Lifehacker, Stern.de, Business Insider, and many others. What was most exciting was seeing the hundreds of online community-run maps in towns and cities across the world. Some coffee shops even hosted copies for their own customers!

It's been my pleasure to get to know each of you guys: the core development team, the contributors, and the thousands that have gotten in touch with me! Niantic, my offer still stands to help you build an official game map!

-Ahmed Almutawa

#### Edit:
Thank you all for the kind words and offers of help! I'd like to clarify that the main reason I chose to shut it down was because I’ve lost interest rather than legal concerns. Niantic’s actions towards 3rd party developers have been very off-putting and it has killed my personal motivation to work on this project. This was a fun weekend project for a game I enjoyed, and now I’ve lost interest in both. I won’t resume development, but there are [active forks of this project][1] you could use.

[1]:	https://github.com/PokemonGoMap/PokemonGo-Map
>>>>>>> AHAAAAAAA/master
