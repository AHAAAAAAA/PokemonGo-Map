var setLabelTime = function(){
    $('.label-countdown').each(function (index, element) {
        var disappearsAt = new Date(parseInt(element.getAttribute("disappears-at")));
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

function pokemonLabel(name, id, disappear_time, latitude, longitude) {
    disappear_date = new Date(disappear_time)
    let pad = number => number <= 99 ? ("0"+number).slice(-2) : number;

    var label = `
        <div>
            <b>${name}</b>
            <span> - </span>
            <small>
                <a href='http://www.pokemon.com/us/pokedex/${id}' target='_blank' title='View in Pokedex'>#${id}</a>
            </small>
        </div>
        <div>
            Disappears at ${pad(disappear_date.getHours())}:${pad(disappear_date.getMinutes())}:${pad(disappear_date.getSeconds())}
            <span class='label-countdown' disappears-at='${disappear_time}'></span></div>
        <div>
            <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}'
                    target='_blank' title='View in Maps'>Get Directions</a>
        </div>`;
    return label;
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
                content: pokemonLabel(item.pokemon_name, item.pokemon_id, item.disappear_time, item.latitude, item.longitude)
            });

            marker.addListener('click', function() {
                marker.infoWindow.open(map, marker);
            });

            console.log(item.latitude);
        });
    });
}
