import SimpleHTTPServer
import SocketServer
import urllib2, json

HOST = '0.0.0.0'
PORT = 8000

CONFIG_URL = 'http://localhost:5000/config'
DATA_URL = 'http://localhost:5000/raw_data'

config = json.loads(urllib2.urlopen(CONFIG_URL).read())
config.update(json.loads(open('credentials.json').read()))

html = '''
<!DOCTYPE html>
<html>
  <head>
	<title>Live Map</title>
	<meta name="viewport" content="initial-scale=1, minimum-scale=1, maximum-scale=1">
	<meta charset="utf-8">
	<style>
		html, body {
			height: 100%%;
			margin: 0;
			padding: 0;
		}
		#map {
			height: 100%%;
		}
	</style>
  </head>
  <body>
	<div id="map"></div>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
	<script>
		var map;
		var infowindow;

		var pokemons = {};

		function tnow() {
			return Math.round(new Date().getTime() / 1000);
		}
		
		function reload() {
			$.getJSON("/rawdata", function(data) {
				console.log(data, tnow());

				for (k in data["pokemons"]) {
					if (k in pokemons) {
						// update
					} else {
						console.log("NEW " + k);
						pokemons[k] = data["pokemons"][k];

						var marker = new google.maps.Marker({
							icon: "/static/icons/" + pokemons[k]["id"] + ".png",
							position: {lat: pokemons[k]["lat"], lng: pokemons[k]["lng"]},
							map: map,
						});

						marker.custom_data = pokemons[k];

						marker.addListener('click', function() {
							var self = this;
							var now = tnow();
							var then = Math.round(self.custom_data["disappear_time"]);
							infowindow.custom_time = then;
							infowindow.setContent("<span style='font-size: 24px;'>" + (then - now) + "</span>");
							infowindow.open(map, self);
						});

						pokemons[k]["marker"] = marker;
					}
				}
				for (k in pokemons) {
					var now = new Date().getTime() / 1000;
					var then = pokemons[k]["disappear_time"];
					if (!(k in data["pokemons"]) || then < now) {
						pokemons[k]["marker"].setMap(null);
						delete pokemons[k];
					}
				}

			});

			setTimeout(reload, 5000);
		}

		function update() {
			var now = tnow();
			var then = infowindow.custom_time;
			infowindow.setContent("<span style='font-size: 24px;'>" + (then - now) + "</span>");
			setTimeout(update, 1000);
		}

		function initMap() {
			map = new google.maps.Map(document.getElementById('map'), {
				center: {lat: %(lat)r, lng: %(lng)r},
				zoom: 15,
			});

			infowindow = new google.maps.InfoWindow({
				content: '',
			});

			infowindow.custom_time = 0;

			update();
			reload();
		}
	</script>
	<script src="https://maps.googleapis.com/maps/api/js?key=%(gmaps_key)r&callback=initMap" async defer></script>
  </body>
</html>
'''

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.wfile.write(html % config)
			self.wfile.close()

		if self.path == '/rawdata':
			self.wfile.write(urllib2.urlopen(DATA_URL).read())
			self.wfile.close()

		if self.path.startswith('/static/'):
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

httpd = SocketServer.TCPServer((HOST, PORT), Handler)

print("Serving at port: %d" % PORT)
httpd.serve_forever()
