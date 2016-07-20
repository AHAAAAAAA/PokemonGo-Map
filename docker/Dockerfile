# Basic docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d -P --name pokemongo-map pokemongo-map -a ptc -u UserName -p Password -l "Seattle, WA" -st 5
FROM gliderlabs/alpine:3.3

MAINTAINER Ahmed Osman (/u/Ashex)

RUN apk add --update openssl ca-certificates
RUN apk add \
    python \
    python-dev \
    py-pip \
    build-base \
    git \
    jq \
  && rm -rf /var/cache/apk/*

RUN pip install geopy==1.11.0 protobuf==2.6.1 requests==2.10.0 flask-googlemaps==0.2.0 s2sphere==0.2.4 flask==0.11.1 gpsoauth==0.3.0 coveralls==1.1 werkzeug==0.11.0
  
WORKDIR /app

EXPOSE 5000
COPY entrypoint.sh .

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]