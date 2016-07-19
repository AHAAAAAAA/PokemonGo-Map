# Basic a docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d --name pokemongo-map pokemongo-map -a ptc -u UserName -p Password -l "Seattle, WA" -st 5
FROM gliderlabs/alpine:3.3

RUN apk add --update openssl ca-certificates
RUN apk add \
    python \
    python-dev \
    py-pip \
    build-base \
    unzip \
    wget \
    git \
  && rm -rf /var/cache/apk/*

RUN pip install geopy protobuf requests flask-googlemaps s2sphere flask gpsoauth coveralls werkzeug
  
WORKDIR /app

EXPOSE 8090
COPY entrypoint.sh .

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]