$(function () {
  var maxDist = 500; // maximium distance to show in meters
  var pokemons = ko.observableArray();
  var nearByPokemon = ko.computed(function () {
    return pokemons()
      .sort(function (a, b) {
        return a.dist() == b.dist() ? 0 : (a.dist() < b.dist() ? -1 : 1);
      })
      .slice(0, 9);
  });
  ko.applyBindings(nearByPokemon);

  function main() {
      if (!navigator.geolocation) return;

      var currentLatLng = ko.observable();
      var lastLatLng;

      function Pokemon(data) {
        var self = this;

        var latLng = new google.maps.LatLng(data.latitude, data.longitude);

        self.num = data.pokemon_id;
        self.sprite = (function () {
          var i = data.pokemon_id - 1;
          var excludedPokemon = JSON.parse(localStorage["remember_select_notify"] || "[]");
          debugger;
          return {
            poisition_x: (i % 7) * -65,
            poisition_y: Math.floor(i / 7) * -65,
            icon_width: 65,
            icon_height: 65,
            shadow: $.inArray(data.pokemon_id, excludedPokemon) >= 0
          }
        })();
        self.name = data.pokemon_name;
        self.dist = ko.computed(function () {
          return google.maps.geometry.spherical.computeDistanceBetween(latLng, currentLatLng());
        });

        return self;
      }

      var rawDataIsLoading = false;
      var loadRawData = function (latLng) {
        var ne = google.maps.geometry.spherical.computeOffset(latLng, maxDist / 2, 0) ;
        ne = google.maps.geometry.spherical.computeOffset(ne, maxDist / 2, 90);
        var se = google.maps.geometry.spherical.computeOffset(ne, maxDist, 180);
        var sw = google.maps.geometry.spherical.computeOffset(se, maxDist, 270);
        //var nw = google.maps.geometry.spherical.computeOffset(sw, maxDist, 0);

        $.ajax({
          url: "/raw_data",
          type: 'GET',
          data: {
            'pokemon': true,
            'pokestops': false,
            'gyms': false,
            'scanned': false,
            'swLat': sw.lat(),
            'swLng': sw.lng(),
            'neLat': ne.lat(),
            'neLng': ne.lng()
          },
          dataType: "json",
          cache: false,
          beforeSend: function () {
            if (rawDataIsLoading) return false;
            else rawDataIsLoading = true;
          },
          complete: function () {
            rawDataIsLoading = false;
          }
        }).then(function (data) {
          $.each(data.pokemons, processPokemon);
        });
      };

      var setTimeoutDate = function (fn, date) {
        var ms = date.getTime() - (new Date()).getTime();
        return setTimeout(fn, ms);
      };

      var processPokemon = function (i, pokemonData) {
        if (!pokemons[pokemonData.encounter_id]) {
          var pokemon = new Pokemon(pokemonData);
          pokemons.push(pokemon);
          pokemons[pokemonData.encounter_id] = pokemon;

          // remove when disappear...
          setTimeoutDate(function () {
            pokemons.remove(pokemon);
            delete pokemons[pokemonData.encounter_id];
          }, new Date(pokemonData.disappear_time));
        }
      };

      var getLatLng = function (position) {
        return new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
      };

      var updateLatLng = function (latLng) {
        return $.post("/next_loc?lat=" + latLng.lat() + "&lon=" + latLng.lng())
          .done(function () {
            lastLatLng = latLng;
          });
      };

      var startWatch = function () {
        navigator.geolocation.watchPosition(function (position) {
          currentLatLng(getLatLng(position));

          //the search function makes any small movements cause a loop. Need to increase resolution
          if (google.maps.geometry.spherical.computeDistanceBetween(lastLatLng, currentLatLng()) > 40) {
            updateLatLng(currentLatLng());
          }
        });

        window.setInterval(function () {
          loadRawData(lastLatLng);
        }, 5000);
        loadRawData(lastLatLng);
      };

      navigator.geolocation.getCurrentPosition(function (position) {
        currentLatLng(getLatLng(position));
        updateLatLng(currentLatLng()).then(startWatch);
      });
  }

  (function waitForGoogle() {
    if (!window.google) setTimeout(waitForGoogle, 10);
    else main();
  })();
});