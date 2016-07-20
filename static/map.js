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
var currentMarker;

//added for places
var sInput;
var searchBox;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: center_lat, lng: center_lng},
        //changed the zoom from 16 to 15
        zoom: 15,
        //default to roadmap
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    setCurrentMarker(center_lat, center_lng, 'initial location');

    sInput = document.getElementById('pac-input');
    searchBox = new google.maps.places.SearchBox(sInput);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(sInput);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });

    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    searchBox.addListener('places_changed', function() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        // For each place, get the icon, name and location.
        var bounds = new google.maps.LatLngBounds();
        places.forEach(function(place) {

            //for now we assume one place, technically this is a for loop
            //so its possible to set current marker multiple times
            setCurrentMarker(place.geometry.location.lat(), place.geometry.location.lng(), place.name);
            
            //lets make a call to the api to change the lat lon, reset the search
            setNewLocation(place.geometry.location.lat(), place.geometry.location.lng());
           
            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });

        //reset the map focus
        map.fitBounds(bounds);
        map.setZoom(15);
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

/**
 * set the current marker location
 * lat = latitude, lng = longitude, title = name of the marker
 */
function setCurrentMarker(lat, lng, title){
    if(currentMarker!=null){
        //clear the marker
        currentMarker.setMap(null);
        currentMarker = null;
    }

    var newLocation={};
    newLocation.lat=lat;
    newLocation.lng=lng;

    currentMarker = new google.maps.Marker({
        position: newLocation,
        map: map,
        title: title,
        animation: google.maps.Animation.DROP
    });
}

/**
 * calls the server api to change the location
 */
function setNewLocation(lat, lng){
    var newLocation={};
    newLocation.lat=lat;
    newLocation.lng=lng;

    $.post("/setLocation", newLocation)
    .fail(function(data){
        alert('failed to call setLocation for: ' + newLocation);
    });
}