var gym_types = [ "Uncontested", "Mystic", "Valor", "Instinct" ];

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

function gymLabel(item) {
    var gym_color = [ "0, 0, 0, .4", "74, 138, 202, .6", "240, 68, 58, .6", "254, 217, 40, .6" ];
    var str;
    if (gym_types[item.team_id] == 0) {
        str = '\
            <div><center>\
            <div>\
                <b style="color:rgba(' + gym_color[item.team_id] + ')">' + gym_types[item.team_id] + '</b><br>\
            </div>\
            </center></div>';
    } else {
        str = '\
            <div><center>\
            <div>\
                Gym owned by:\
            </div>\
            <div>\
                <b style="color:rgba(' + gym_color[item.team_id] + ')">Team ' + gym_types[item.team_id] + '</b><br>\
                <img height="100px" src="/static/forts/' + gym_types[item.team_id] + '_large.png"> \
            </div>\
            <div>\
                Prestige: ' + item.gym_points + '\
            </div>\
            </center></div>';
    }

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

            marker.addListener('click', function() {
                marker.infoWindow.open(map, marker);
            });

            console.log(item.latitude);
        });
    });

    $.getJSON("/gyms", function(result){
        $.each(result, function(i, item){
            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/forts/'+gym_types[item.team_id]+'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content: gymLabel(item)
            });

            marker.addListener('click', function() {
                marker.infoWindow.open(map, marker);
            });
        });
    });
}
