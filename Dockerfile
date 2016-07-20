FROM python:2.7
MAINTAINER github.com/jshapiro26

WORKDIR /opt/pokemongo-map
ADD locales locales
ADD static static
ADD templates templates
ADD credentials.json credentials.json
ADD example.py example.py
ADD pokemon.proto pokemon.proto
ADD pokemon_pb2.py pokemon_pb2.py
ADD requirements.txt requirements.txt
ADD transform.py transform.py
RUN pip install -r requirements.txt