# Basic Installation

## In-Depth

If any of the following guides apply to you, click those instead:

  * [WINDOWS INSTRUCTIONS](Windows-Installation-and-requirements.md)

  * [MAC INSTRUCTIONS](Macintosh-Installation-and-requirements.md)

  * [HEROKU INSTRUCTIONS](heroku.md)

  * [BLUEMIX INSTRUCTIONS](bluemix.md)

  * [DigitalOcean Instructions](digitalocean.md)

## Prerequisites

Installation will require Python 2.7 and Pip. If you already have these you can skip to [installation](#install-dependencies). Python 3 is not supported at all.

### Ubuntu

You can install the required packages on Ubuntu by running the following command:

```
sudo apt-get install python python-pip nodejs npm
```

### Debian

You can install the required packages on Debian by running the following command:

```
sudo apt-get install python python-pip nodejs npm nodejs-legacy
```

### Red Hat or CentOs or Fedora

You can install required packages on Red Hat by running the following command:

You may also need to install the EPEL repository to install python-pip and python-devel.
```
yum install epel-release
```

```
yum install python python-pip nodejs npm python-devel
```

### OS X

OS X comes with some outdated Python packages.

You will need to install `pip`, then upgrade a few python packages. 

Instructions (run everything, each on its own line):

```
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
sudo python ./get-pip.py
sudo -H easy_install --upgrade six
sudo -H easy_install --upgrade setuptools
```

To install node and npm, download and install the installer from https://nodejs.org/en/download/.



### Windows

Download Python [here](https://www.python.org/ftp/python/2.7.12/python-2.7.12.amd64.msi) and install. Then download [pip](https://bootstrap.pypa.io/get-pip.py) (right click that link and choose "Save Link As"), and double click the file you downloaded, assuming you installed Python correctly.

Download NodeJS [here](https://nodejs.org/en/download/) and install.

There is a one-click setup for Windows. After you've installed Python, go into the `Easy Setup` folder and run `setup.bat`. This should install `pip` and the dependencies for you, and put your Google API key into the right place.

## Credentials and Downloading

Create a Pokemon Club account [on their official website] to be used by the program to search for Pokemon. This generally shouldn't be the same as your main Trainer account you personally use. As of 7/21/2016 this page is unavailable most of the time, refresh the page every 5-10 minutes and it should allow signups eventually.
You can also use a Google account. For both services, you can login without ever connecting to the actual game. 

Then, download one of the following branches below:

- [Download master](https://github.com/AHAAAAAAA/PokemonGo-Map/archive/master.zip) (Stable builds)
- [Download dev branch](https://github.com/AHAAAAAAA/PokemonGo-Map/archive/develop.zip) (Active development)

The dev branch will have latest features from the development team, however it may be unstable at some times.

Extract this zip file to any location.


## Installing required python and nodejs modules 

At this point you should have the following:

* Python 2.7 installed
* pip installed
* Unpacked archive of PokemonGo-Map
* [nodejs](https://nodejs.org/en/download/) installed

Open up your shell and change to the directory of PokemonGo-Map then run the following commands:

Linux: 

```bash
sudo -H pip install -r requirements.txt
sudo npm install -g grunt
npm install
npm run-script build
```

Windows:

```bash
pip install -r requirements.txt
npm install -g grunt
npm install
npm run-script build
```

Result:

```
$ python ./runserver.py --help
usage: runserver.py [-h] [-se] [-a AUTH_SERVICE] [-u USERNAME] [-p PASSWORD]
                    [-l LOCATION] [-st STEP_LIMIT] [-sd SCAN_DELAY] [-dc]
                    [-H HOST] [-P PORT] [-L LOCALE] [-c] [-d] [-m] [-ns]
                    [-k GMAPS_KEY] [-C] [-D DB] [-t NUM_THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -se, --settings
  -a AUTH_SERVICE, --auth-service AUTH_SERVICE
                        Auth Service
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password
  -l LOCATION, --location LOCATION
                        Location, can be an address or coordinates
  -st STEP_LIMIT, --step-limit STEP_LIMIT
                        Steps
  -sd SCAN_DELAY, --scan-delay SCAN_DELAY
                        Time delay before beginning new scan
  -dc, --display-in-console
                        Display Found Pokemon in Console
  -H HOST, --host HOST  Set web server listening host
  -P PORT, --port PORT  Set web server listening port
  -L LOCALE, --locale LOCALE
                        Locale for Pokemon names: default en, checklocale
                        folder for more options
  -c, --china           Coordinates transformer for China
  -d, --debug           Debug Mode
  -m, --mock            Mock mode. Starts the web server but not the
                        background thread.
  -ns, --no-server      No-Server Mode. Starts the searcher but not the
                        Webserver.
  -k GMAPS_KEY, --google-maps-key GMAPS_KEY
                        Google Maps Javascript API Key
  -C, --cors            Enable CORS on web server
  -D DB, --db DB        Database filename
  -t NUM_THREADS, --threads NUM_THREADS
                        Number of search threads
```

## Google Maps API key

You will need to generate your own Google Maps API key and place it in your program directory to use this program. Here's a [wiki entry](GoogleMaps.md) on how to do this part.

## Running

To start the server, run the following command:

```
python runserver.py -u [USERNAME] -p [PASSWORD] -st 10 -k [Google Maps API key] -l "[LOCATION]"
```

or for Google account:

```
python runserver.py -a google -u [USERNAME] -p [PASSWORD] -st 10 -k [Google Maps API key] -l "[LOCATION]" 
```

Replacing [USERNAME] and [PASSWORD] with the Pokemon Club credentials you created previously, and [LOCATION] with any location, for example `Washington, D.C` or latitude and longitude coordinates, such as `38.9072 77.0369`.

Additionally, you can change the `10` after `-st` to any number. This number indicates the number of steps away from your location it should look, higher numbers being farther.

## Accessing

Open your browser to [`http://localhost:5000`](http://localhost:5000) and keep refreshing as it loads more Pokemon (auto refresh is not implemented yet).
