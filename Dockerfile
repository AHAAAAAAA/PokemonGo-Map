# Basic docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d -P pokemongo-map --host 0.0.0.0 -a ptc -u YOURUSERNAME -p YOURPASSWORD -l "Seattle, WA" -st 10 --google-maps-key CHECKTHEWIKI

FROM python:2.7-alpine

# keep this near the top of the file since we'll always need this
# ca-certificates is needed because without it, pip fails to install packages due to a certificate failure
RUN apk add --no-cache \
    ca-certificates

# default port the app runs on
EXPOSE 5000

WORKDIR /usr/src/app

ENTRYPOINT ["python", "./runserver.py"]

# Copy Python requirements so we only rebuild deps if they have changed
COPY requirements.txt /usr/src/app/

# build-base contains gcc, which is needed during the installation of the pycryptodomex pip package
RUN apk add --no-cache \
    build-base \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del build-base

# Add the rest of the app code
COPY . /usr/src/app
