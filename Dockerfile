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

# add certificates to talk to the internets
RUN apk add --no-cache ca-certificates

# Copy Python requirements so we only rebuild deps if they have changed
COPY requirements.txt /usr/src/app/

# Install all prerequisites (build base used for gcc of some python modules)
RUN apk add --no-cache build-base nodejs \
 && pip install --no-cache-dir -r requirements.txt
 
COPY package.json /usr/src/app/

RUN npm install

# Add the rest of the app code
COPY . /usr/src/app

# Let grunt do its magic
RUN npm install -g grunt \
    && grunt jshint sass cssmin uglify \
    && npm remove -g grunt \
    && npm cache clean \
    && rm -rf node_modules \
    && apk del build-base
    && rm package.json
    && rm Gruntfile.js