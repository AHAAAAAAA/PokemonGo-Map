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

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache build-base \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del build-base

COPY package.json Gruntfile.js /usr/src/app/
COPY static /usr/src/app/static

RUN apk add --no-cache build-base nodejs \
 && npm install -g grunt-cli \
 && npm install \
 && npm run-script build \
 && npm uninstall -g grunt-cli \
 && rm -rf node_modules \
 && apk del build-base nodejs

# Copy everything to the working directory (Python files, templates, config) in one go.
COPY . /usr/src/app/
