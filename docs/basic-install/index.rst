Basic Installation
##################

Follow one of the guides below to get the basic pre-requisits installed:

.. toctree::
    :maxdepth: 1
    :glob:

    osx
    windows
    linux
    google-maps

Credentials and Downloading
***************************

Register either a Pokemon Club account or a Google account to use with the map. Do not use your main account.

Then, download one of the following branches below:

 * `Master <https://github.com/AHAAAAAAA/PokemonGo-Map/archive/master.zip>`_ (Stable Builds)
 * `Develop <https://github.com/AHAAAAAAA/PokemonGo-Map/archive/develop.zip>`_ (Active Development)

The ``develop`` branch will have latest features from the development team, however it may be unstable at some times.

Extract this zip file to any location.

Installing Modules
******************

At this point you should have the following:

* Python 2.7
* pip
* nodejs
* Unpacked archive of PokemonGo-Map

Open up your shell and change to the directory of PokemonGo-Map then run the following commands:

Linux:

.. code-block:: bash

  sudo -H pip install -r requirements.txt
  sudo npm install -g grunt
  npm install
  npm run-script build

Windows:

.. code-block:: bash

  pip install -r requirements.txt
  npm install -g grunt
  npm install
  npm run-script build

Once those have run, you should be able to start using the application, like so:

.. code-block:: bash

  python ./runserver.py --help

Read through the available options and set all the required CLI flags to start your own server. At a minimum you will need to provide a location, account login credentials, and a :doc:`google maps key <google-maps>`.

Accessing
*********

Open your browser to http://localhost:5000 and your pokemon will begin to show up! Happy hunting!
