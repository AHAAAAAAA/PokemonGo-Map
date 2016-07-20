
function pokemonLabel(name, disappear_time, id, disappear_time, latitude, longitude) {
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
            <span class='label-countdown' disappears-at='${disappear_time}'>(00m00s)</span></div>
        <div>
            <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}' 
                    target='_blank' title='View in Maps'>Get Directions</a>
        </div>`;
    return label;
}


var map;
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: center_lat, lng: center_lng},
    zoom: 16
  });
}

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


