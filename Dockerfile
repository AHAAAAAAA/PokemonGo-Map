# Basic docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d -P --name pokemongo-map pokemongo-map -a ptc -u UserName -p Password -l "Seattle, WA" -st 10 --google-maps-key CHECKTHEWIKI
FROM gliderlabs/alpine:3.3

MAINTAINER Ahmed Osman (/u/Ashex)

EXPOSE 5000

RUN apk add --update ca-certificates
RUN apk add \
    python \
    python-dev \
    py-pip \
    build-base \
  && rm -rf /var/cache/apk/*

COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/bin/python", "runserver.py", "--host", "0.0.0.0"]
