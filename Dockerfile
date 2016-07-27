# Basic docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d -P pokemongo-map -a ptc -u YOURUSERNAME -p YOURPASSWORD -l "Seattle, WA" -st 10 --gmaps-key CHECKTHEWIKI

FROM python:2.7-alpine

# Default port the webserver runs on
EXPOSE 5000

# Working directory for the application
WORKDIR /usr/src/app

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python", "./runserver.py", "--host", "0.0.0.0"]

# Set default options when container is run without any command line arguments
CMD ["-h"]

# Install required system packages
RUN apk add --no-cache ca-certificates

# Since we're changing requirements and css so often now, it's almost guaranteed
# that SOMETHING which requires a rebuild needs to be redone. As such, and to
# optimize layers for distribution, this will copy in everything in a go.
COPY . /usr/src/app/

# Get it all installed and built then remove the build systems
RUN apk add --no-cache build-base nodejs \
 && pip install --no-cache-dir -r requirements.txt \
 && npm install -g grunt-cli \
 && npm install \
 && npm run-script build \
 && npm uninstall -g grunt-cli \
 && rm -rf node_modules \
 && apk del build-base nodejs
