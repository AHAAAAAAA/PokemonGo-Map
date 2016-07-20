function pokemonLabel(name, disappear_time, id, disappear_time, latitude, longitude) {
    disappear_date = new Date(disappear_time)

    var pad = function pad(number) {
      return number <= 99 ? ("0" + number).slice(-2) : number;
    };

    var str = '\
        <div>\
            <b>' + name + '</b>\
            <span> - </span>\
            <small>\
                <a href="http://www.pokemon.com/us/pokedex/' + id + '" target="_blank" title="View in Pokedex">#' + id + '</a>\
            </small>\
        </div>\
        <div>\
            Disappears at ' + pad(disappear_date.getHours()) + ':' + pad(disappear_date.getMinutes()) + ':' + pad(disappear_date.getSeconds()) + '\
            <span class="label-countdown" disappears-at="' + disappear_time + '">(00m00s)</span></div>\
        <div>\
            <a href="https://www.google.com/maps/dir/Current+Location/' + latitude + ',' + longitude + '"\
                    target="_blank" title="View in Maps">Get Directions</a>\
        </div>';

    return str;
}


var map;
var marker;
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: center_lat, lng: center_lng},
        zoom: 16
    });
    marker = new google.maps.Marker({
        position: {lat: center_lat, lng: center_lng},
        map: map,
        animation: google.maps.Animation.DROP
    });

    initPokemon();
    console.log(display_gyms);
    if(display_gyms) {
      initGyms();
    }
}


function initPokemon() {
  $.getJSON("/pokemons", function(result){
      $.each(result, function(i, item){

          var marker = new google.maps.Marker({
              position: {lat: item.latitude, lng: item.longitude},
              map: map,
              icon: 'static/icons/'+item.pokemon_id+'.png'
          });

          marker.infoWindow = new google.maps.InfoWindow({
              content: pokemonLabel(item.pokemon_name, item.disappear_time, item.pokemon_id, item.disappear_time, item.latitude, item.longitude)
          });

          google.maps.event.addListener(marker.infoWindow, 'closeclick', function(){
              delete marker["persist"];
              marker.infoWindow.close();
          });

          marker.addListener('click', function() {
              marker["persist"] = true;
              marker.infoWindow.open(map, marker);
          });

          marker.addListener('mouseover', function() {
              marker.infoWindow.open(map, marker);
          });

          marker.addListener('mouseout', function() {
              if (!marker["persist"]) {
                  marker.infoWindow.close();
              }
          });

          console.log(item.latitude);
      });
  });
}

function initGyms() {
  $.getJSON("/gyms", function(result) {
    $.each(result, function(i, item) {
      var icon;
      switch(item.team_id) {
        case 0: icon = 'static/forts/Gym.png'; break;
        case 1: icon = 'static/forts/Mystic.png'; break;
        case 2: icon = 'static/forts/Valor.png'; break;
        case 3: icon = 'static/forts/Instinct.png'; break;
      }

      var marker = new google.maps.Marker({
        position: {lat: item.latitude, lng: item.longitude},
        map: map,
        icon: icon
      });
    })
  });
}
