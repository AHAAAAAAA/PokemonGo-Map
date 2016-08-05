# Docker

Docker is a great way to run "containerized" applications easily and without installing tons of stuff into your computer.

## Prerequisits

To get started, [install Docker by following their instructions](https://www.docker.com/products/docker).

## First Install

For your first install, there's only a few steps. Let's get to it!

### Start the Map 

You'll need to change the command line params. If you don't know what they are, you can run `docker run --rm chuyskywalker/pokemongo-map -h` and you'll get the full help text. The command below examples out a very basic setup.

```
docker run -d --name pogomap \
  chuyskywalker/pokemongo-map \
    -a ptc -u your -p login \
    -k 'google-maps-key' \
    -l 'coords' \
    -st 5
```

If you've like to see that the application is outputting (console logs) you can run `docker logs -f pogomap` and just type `ctrl-c` when you're done watching.

### Start an SSL Tunnel

At this point, the map is running, but you can't get to it. Also, you'll probably want to access this from places other than `localhost`. Finally, if you want location services to work, you'll need SSL.

We'll use [ngrok](https://ngrok.com/) to make a secure tunnel to solve all of those issues!

```
docker run -d --name ngrok --link pogomap \
  wernight/ngrok \
    ngrok http pogomap:5000
```

### Discover ngrok URL

Now that ngrok tunnel is running, let's see what domain you've been assigned. You can run this command to grab it from the ngrok instance

```
docker run --rm --link ngrok \
  appropriate/curl \
    sh -c "curl -s http://ngrok:4040/api/tunnels | grep -o 'https\?:\/\/[a-zA-Z0-9\.]\+'"
```

That should return something like:

```
http://random-string-here.ngrok.io
https://random-string-here.ngrok.io
```

Open that up and you're ready to rock!

## Updating Versions

When you update, you remove all the current containers, pull the latest version, and restart everything.

Run:

```
docker rm -f pogomap ngrok
docker pull chuyskywalker/pokemongo-map
```

Then redo the steps from "First Install" and you'll be on the latest version!

## Running on docker cloud 

If you want to run pokemongo-map on a service that doesn't support arguments like docker cloud or ECS, you'll need to use one of the more specialised images out there that supports variables. The image `ashex/pokemongo-map` handles variables, below is an example:

```bash
  docker run -d -P \
    -e "AUTH_SERVICE=ptc" \
    -e "USERNAME=UserName" \
    -e "PASSWORD=Password" \
    -e "LOCATION=Seattle, WA" \
    -e "STEP_LIMIT=5" \
    -e "GMAPS_KEY=SUPERSECRET" \
    ashex/pokemongo-map
```