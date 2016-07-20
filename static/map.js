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
            <span class="label-countdown" disappears-at="' + disappear_time/1000 + '">(00m00s)</span></div>\
        <div>\
            <a href="https://www.google.com/maps/dir/Current+Location/' + latitude + ',' + longitude + '"\
                    target="_blank" title="View in Maps">Get Directions</a>\
        </div>';

    return str;
}

function pokestopLabel(lure_expiration) {
    expiration_date = new Date(lure_expiration)

    var pad = function pad(number) {
      return number <= 99 ? ("0" + number).slice(-2) : number;
    };

    if (lure_expiration > 0)
        var str = 'Lured Pokestop, expires at ' + pad(expiration_date.getHours()) + ':' + pad(expiration_date.getMinutes()) + ':' + pad(expiration_date.getSeconds());
    else
        var str = 'Pokestop';

    return str;
}

function gymLabel(team_id, team) {

    switch (team_id)
    {
        case 1: var color = 'rgba(74, 138, 202, .6)'; break;
        case 2: var color = 'rgba(240, 68, 58, .6)'; break;
        case 3: var color = 'rgba(254, 217, 40, .6)'; break;
        default: var color = 'rgba(200, 200, 200, .6)';
    }

    var str = '<div><center><small>Gym owned by:</small><br> \
    <b style=\'color:'+color+'\'>Team '+team+'</b> \
    <br><img id=\''+team+'\' height=\'100px\' src=\'static/forts/'+team+'_large.png\'></center>';

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

    $.getJSON("/pokestops", function(result){
        $.each(result, function(i, item){

            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/forts/'+(item.lure_expiration > 0 ? 'PstopLured' : 'Pstop')+'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content: pokestopLabel(item.lure_expiration)
            });

            marker.addListener('click', function() {
                marker.infoWindow.open(map, marker);
            });

            console.log(item.latitude);
        });
    });

    $.getJSON("/gyms", function(result){
        $.each(result, function(i, item){

            switch (item.team_id)
            {
                case 1: var team = 'Mystic'; break;
                case 2: var team = 'Valor'; break;
                case 3: var team = 'Instinct'; break;
                default: var team = 'Uncontested';
            }

            var marker = new google.maps.Marker({
                position: {lat: item.latitude, lng: item.longitude},
                map: map,
                icon: 'static/forts/'+team+'.png'
            });

            marker.infoWindow = new google.maps.InfoWindow({
                content:  gymLabel(item.team_id, team)
            });

            marker.addListener('click', function() {
                marker.infoWindow.open(map, marker);
            });

            console.log(item.latitude);
        });
    });
}

var setLabelTime = function(){
    $('.label-countdown').each(function (index, element) {
        var disappearsAt = new Date(parseInt(element.getAttribute("disappears-at"))*1000);
        var now = new Date();

        var difference = Math.abs(disappearsAt - now);
        var hours = Math.floor(difference / 36e5);
        var minutes = Math.floor((difference - (hours * 36e5)) / 6e4);
        var seconds = Math.floor((difference - (hours * 36e5) - (minutes * 6e4)) / 1e3);

        if(disappearsAt < now){
            timestring = "(expired)";
        }
        else {
            timestring = "(";
            if(hours > 0)
                timestring = hours + "h";

            timestring += ("0" + minutes).slice(-2) + "m";
            timestring += ("0" + seconds).slice(-2) + "s";
            timestring += ")";
        }

        $(element).text(timestring)
    });
};

window.setInterval(setLabelTime, 1000);