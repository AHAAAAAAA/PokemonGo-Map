# Basic docker image for PokemonGo-Map
# Usage:
#   docker build -t pokemongo-map .
#   docker run -d -P pokemongo-map -a ptc -u YOURUSERNAME -p YOURPASSWORD -l "Seattle, WA" -st 10 --google-maps-key CHECKTHEWIKI

FROM python:2.7-alpine

# Default port the webserver runs on
EXPOSE 5000

# Working directory for the application
WORKDIR /usr/src/app

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python", "./runserver.py", "--host", "0.0.0.0"]

# Set default options when container is run without any command line arguments
CMD ["-h"]

# build-base contains gcc, which is needed during the installation of the pycryptodomex pip package
RUN apk add --no-cache \
    build-base ca-certificates

# Copy Python requirements so we only rebuild deps if they have changed
COPY requirements.txt /usr/src/app/

# Install all prerequisites
RUN pip install --no-cache-dir -r requirements.txt \
 && apk del build-base

# Add the rest of the app code
COPY . /usr/src/app
