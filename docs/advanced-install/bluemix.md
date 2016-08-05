# Bluemix

[Bluemix](http://bluemix.net) is IBM's PaaS, built on top of
[Cloud Foundry](https://www.cloudfoundry.org/), and it's free tier allows you 
to have 24 up time! Oh boy!

## Prerequisites

  1. Clone the git repo via `https://github.com/AHAAAAAAA/PokemonGo-Map.git`
  1. Create a [Bluemix](http://bluemix.net) account
  1. Install the [Cloud Foundry CLI](https://console.ng.bluemix.net/docs/cli/reference/cfcommands/index.html)

## Create and Run the App on Bluemix

To do this, you can either use the GUI (click through, create a new python
runtime and name it). Once it's created, you push the code by `cd`ing into the
directory and running:

    cf push <nameofapp>

To do the same thing via command line, you simply run that last command. It'll
create the app and push the code for you.

Note that this first deploy will fail! We need to configure the environment
variables for authentication to Pokemon Go and your Google API Key. To do that
via the CLI:

    cf set-env <nameofapp> AUTH_SERVICE <ptc|google>
    cf set-env <nameofapp> USERNAME <username>
    cf set-env <nameofapp> PASSWORD <password>
    cf set-env <nameofapp> GMAPS_KEY <your google api key>
    cf set-env <nameofapp> STEP_COUNT <step count>
    cf set-env <nameofapp> LOCATION <the location you're spying on>

To set the environment variables via the GUI, you navigate to the "environment
variables" tab in the app dashboard, click on "user defined," and enter them one
by one.

Also make sure to paste your google api key in `config/credentials.json`.

Once the environment variables are set, and your credentials are set in
`config/credentials.json`, re-push via `cf push <nameofapp>`.

## An alternate way to set your credentials

Alternatively, instead of going the environment variable route, you can set up
`config/config.ini`, and change the start command in `manifest.yml` to be

    python runserver.py -se

which will pull the values from the config file instead of from the env vars.
