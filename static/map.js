var map,
    marker,
    locationMarker,
    lastStamp = 0,
    requestInterval = 10000;

var markers = [];
var gym_types = [ "Uncontested", "Mystic", "Valor", "Instinct" ];

function pad(number) {
    return number <= 99 ? ("0" + number).slice(-2) : number;
};

pokemonLabel = function(item) {
    disappear_date = new Date(item.disappear_time);

    var str = '\
        <div>\
            <b>' + item.pokemon_name + '</b>\
            <span> - </span>\
            <small>\
                <a href="http://www.pokemon.com/us/pokedex/' + item.pokemon_id + '" target="_blank" title="View in Pokedex">#' +item.pokemon_id + '</a>\
            </small>\
        </div>\
        <div>\
            Disappears at ' + pad(disappear_date.getHours()) + ':' + pad(disappear_date.getMinutes()) + ':' + pad(disappear_date.getSeconds()) + '\
            <span class="label-countdown" disappears-at="' + item.disappear_time + '"></span></div>\
        <div>\
            <a href="https://www.google.com/maps/dir/Current+Location/' + item.latitude + ',' + item.longitude + '"\
                    target="_blank" title="View in Maps">Get Directions</a>\
        </div>';

    return str;
};

gymLabel = function gymLabel(item) {
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
                <img height="100px" src="static/forts/' + gym_types[item.team_id] + '_large.png"> \
            </div>\
            <div>\
                Prestige: ' + item.gym_points + '\
            </div>\
            </center></div>';
    }

    return str;
};

pokestopLabel = function pokestopLabel(item) {
    var str;

    if (!item.lure_expiration) {
        str = '<div><center> \
                   <div><b>Pokéstop</b></div> \
               </center></div>';
    } else {
        expire_date = new Date(item.lure_expiration)
        str = '<div><center> \
                   <div><b>Pokéstop</b></div> \
                   <div><b>Lure enabled</b></div> \
                   Expires at ' + pad(expire_date.getHours()) + ':' + pad(expire_date.getMinutes()) + ':' + pad(expire_date.getSeconds()) + '\
                   <span class="label-countdown" disappears-at="' + item.lure_expiration + '"></span></div>\
               </center></div>';
    }
    return str;
}

myLocationButton = function (map, marker) {
    var locationContainer = document.createElement('div');

    var locationButton = document.createElement('button');
    locationButton.style.backgroundColor = '#fff';
    locationButton.style.border = 'none';
    locationButton.style.outline = 'none';
    locationButton.style.width = '28px';
    locationButton.style.height = '28px';
    locationButton.style.borderRadius = '2px';
    locationButton.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    locationButton.style.cursor = 'pointer';
    locationButton.style.marginRight = '10px';
    locationButton.style.padding = '0px';
    locationButton.title = 'Your Location';
    locationContainer.appendChild(locationButton);

    var locationIcon = document.createElement('div');
    locationIcon.style.margin = '5px';
    locationIcon.style.width = '18px';
    locationIcon.style.height = '18px';
    locationIcon.style.backgroundImage = 'url(static/mylocation-sprite-1x.png)';
    locationIcon.style.backgroundSize = '180px 18px';
    locationIcon.style.backgroundPosition = '0px 0px';
    locationIcon.style.backgroundRepeat = 'no-repeat';
    locationIcon.id = 'current-location';
    locationButton.appendChild(locationIcon);

    locationButton.addEventListener('click', function() {
        var currentLocation = document.getElementById('current-location');
        var imgX = '0';
        var animationInterval = setInterval(function(){
            if(imgX == '-18') imgX = '0';
            else imgX = '-18';
            currentLocation.style.backgroundPosition = imgX+'px 0';
        }, 500);
        if(navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                locationMarker.setVisible(true);
                locationMarker.setOptions({'opacity': 1});
                locationMarker.setPosition(latlng);
                map.setCenter(latlng);
                clearInterval(animationInterval);
                currentLocation.style.backgroundPosition = '-144px 0px';
            });
        }
        else{
            clearInterval(animationInterval);
            currentLocation.style.backgroundPosition = '0px 0px';
        }
    });

    locationContainer.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(locationContainer);
}

addMyLocationButton = function () {
    locationMarker = new google.maps.Marker({
        map: map,
        animation: google.maps.Animation.DROP,
        position: {lat: center_lat, lng: center_lng},
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 1,
            fillColor: '#1c8af6',
            scale: 6,
            strokeColor: '#1c8af6',
            strokeWeight: 8,
            strokeOpacity: 0.3
        }
    });
    locationMarker.setVisible(false);

    myLocationButton(map, locationMarker);

    google.maps.event.addListener(map, 'dragend', function() {
        var currentLocation = document.getElementById('current-location');
        currentLocation.style.backgroundPosition = '0px 0px';
        locationMarker.setOptions({'opacity': 0.5});
    });
}

initMap = function() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: center_lat, lng: center_lng},
        zoom: 16
    });
    var marker = new google.maps.Marker({
        position: {lat: center_lat, lng: center_lng},
        map: map,
        animation: google.maps.Animation.DROP
    });
    addMyLocationButton();
    GetNewPokemons(lastStamp);
    GetNewGyms();
    GetNewPokeStops();
};

GetNewPokemons = function(stamp) {
    $.getJSON("pokemons/"+stamp, function(result){
        $.each(result, function(i, item){

            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/icons/'+item.pokemon_id+'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content: pokemonLabel(item)
            });

            google.maps.event.addListener(marker.infoWindow, 'closeclick', function(){
                delete marker["persist"];
                marker.infoWindow.close();
            });

            marker.addListener('click', function() {
                marker["persist"] = true;
                marker.infoWindow.open(map, marker);
            });

            markers.push({
                    m: marker,
                    disapear: item.disappear_time});

            marker.addListener('mouseover', function() {
                marker.infoWindow.open(map, marker);
            });

            marker.addListener('mouseout', function() {
                if (!marker["persist"]) {
                    marker.infoWindow.close();
                }
            });
        });
    }).always(function() {
        setTimeout(function() {
            GetNewPokemons(lastStamp);
            GetNewGyms();
            GetNewPokeStops();
        }, requestInterval)
    });

    var dObj = new Date();
    lastStamp = dObj.getTime();

    $.each(markers, function(i, item){
        if (item.disapear <= lastStamp - (dObj.getTimezoneOffset() * 60000))
            item.m.setMap(null);
    });
};

GetNewGyms = function() {
    $.getJSON("gyms", function(result){
        $.each(result, function(i, item){
            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/forts/'+gym_types[item.team_id]+'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content: gymLabel(item)
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
        });
    });
};

GetNewPokeStops = function() {
    $.getJSON("pokestops", function(result){
        $.each(result, function(i, item){
            var imagename = item.lure_expiration ? "PstopLured" : "Pstop";
            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/forts/'+ imagename +'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content: pokestopLabel(item)
            });

            if (item.lure_expiration) {
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
            } else {
                marker.addListener('click', function() {
                    marker.infoWindow.open(map, marker);
                });
            }
        });
    });
};

var setLabelTime = function(){
$('.label-countdown').each(function (index, element) {
    var now = new Date().getTime();
    var diff = element.getAttribute("disappears-at") - now;

    if (diff > 0) {
        var min = Math.floor((diff / 1000) / 60);
        var sec = Math.floor((diff / 1000) - (min * 60));
        $(element).text("(" + pad(min) + "m" + pad(sec) + "s" + ")");
    } else {
        $(element).text("(Gone!)");
    }


    });
};

window.setInterval(setLabelTime, 1000);
