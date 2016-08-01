var rawDataIsLoading = false;
var detailsLoading = false;
var total = 0;
var detailInterval = null;
var lastappearance = 1;
var totalPokemon = 151;
var pokemonid = 0;
var monthArray = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var mapLoaded = false;
var detailsPersist = false;
map_data.appearances = {};

function loadRawData(){
    return $.ajax({
        url: "raw_data",
        type: 'GET',
        data: {
            'pokemon': false,
            'pokestops': false,
            'gyms': false,
            'scanned': false,
            'seen': true,
            'duration': document.getElementById('duration').options[document.getElementById('duration').selectedIndex].value
        },
        dataType: "json",
        beforeSend: function() {
            if (rawDataIsLoading) {
                return false;
            } else {
                rawDataIsLoading = true;
            }
        },
        complete: function() {
            rawDataIsLoading = false;
        }
    })
}

function loadDetails(){
    return $.ajax({
        url: "raw_data",
        type: 'GET',
        data: {
            'pokemon': false,
            'pokestops': false,
            'gyms': false,
            'scanned': false,
            'appearances': true,
            'pokemonid': pokemonid,
            'last': lastappearance
        },
        dataType: "json",
        beforeSend: function() {
            if (detailsLoading) {
                return false;
            } else {
                detailsLoading = true;
            }
        },
        complete: function() {
            detailsLoading = false;
        }
    })
}

function showTimes(marker){
    uuid = marker.position.lat().toFixed(7) + "_" + marker.position.lng().toFixed(7);
    $('#times_list').html(appearanceLabel(map_data.appearances[uuid]));
    $('#times_list').show();
}

function closeTimes(){
    $('#times_list').hide();
    detailsPersist = false;
}

//Overrides addListeners in map.js
function addListeners(marker){

    marker.addListener('click', function() {
        showTimes(marker);
        detailsPersist = true;
      });

      marker.addListener('mouseover', function() {
        showTimes(marker);
      });

      marker.addListener('mouseout', function() {
        if(!detailsPersist)
            $('#times_list').hide();
      });

    return marker;
}

function processTotal(seen){
    total = 0;
    for(var i = 0; i < seen.length; i++)
        total += seen[i].count;

    document.getElementById("seen_total").innerHTML = 'Total: ' + total.toLocaleString();
}

function processSeen(seen){
    var total = 0;
    var shown = Array();

    seen.sort(function(a, b){
        var sort = document.getElementById("sort");
        var order = document.getElementById("order");

        if(order.options[order.selectedIndex].value == "desc"){
            var tmp = b;
            b = a;
            a = tmp;
        }

        if(sort.options[sort.selectedIndex].value == "id"){
            return a.pokemon_id-b.pokemon_id;
        }else if(sort.options[sort.selectedIndex].value == "name"){
            if(a.pokemon_name.toLowerCase() < b.pokemon_name.toLowerCase()) return 1;
            if(a.pokemon_name.toLowerCase() > b.pokemon_name.toLowerCase()) return -1;
            return 0;
        }else{
            //Default to count
            if(a.count == b.count) //Same count: order by id
                return b.pokemon_id-a.pokemon_id;

            return a.count-b.count;
        }

    });

    for(var i = 0; i < seen.length; i++)
        total += seen[i].count;

    for(var i = seen.length - 1; i >= 0; i--){
        var item = seen[i];
        var percentage = (item.count / total * 100).toFixed(2);
        var lastSeen = new Date(item.disappear_time);
        lastSeen =  lastSeen.getHours() + ':' +
                    ("0" + lastSeen.getMinutes()).slice(-2) + ':' +
                    ("0" + lastSeen.getSeconds()).slice(-2) + ' ' +
                    lastSeen.getDate() + ' ' +
                    monthArray[lastSeen.getMonth()] + ' ' +
                    lastSeen.getFullYear();
        var location = (item.latitude * 1).toFixed(7) + ', ' + (item.longitude * 1).toFixed(7);
        if(!$('#seen_' + item.pokemon_id).length)
            addElement(item.pokemon_id, item.pokemon_name);
        $('#count_' + item.pokemon_id).html('Seen: ' + item.count.toLocaleString() + ' (' + percentage + '%)');
        $('#lastseen_' + item.pokemon_id).html('Last Seen: ' + lastSeen);
        $('#location_' + item.pokemon_id).html('Location: ' + location);
        $('#seen_' + item.pokemon_id).show();
        //Reverting to classic javascript here as it's supposed to increase performance
        document.getElementById('seen_container').insertBefore(document.getElementById('seen_' + item.pokemon_id), document.getElementById('seen_container').childNodes[0]);
        shown.push(item.pokemon_id);
    }

    //Hide any unneeded items
    for(var i = 1; i <= this.totalPokemon; i++){
        if(shown.indexOf(i) < 0)
            $('#seen_' + i).hide();
    }

    document.getElementById("seen_total").innerHTML = 'Total: ' + total.toLocaleString();
}

//Override UpdateMap in map.js to take advantage of a pre-existing interval.
function updateMap(){
    var duration = document.getElementById("duration");
    var header = 'Pokemon Seen in ' + duration.options[duration.selectedIndex].text;
    if($('#seen_header').html() != header){
            $('#seen_container').hide();
            $('#loading').show();
            $('#seen_header').html('');
            $('#seen_total').html('');
    }
    loadRawData().done(function (result) {
        processSeen(result.seen);
        if($('#seen_header').html() != header){
            $('#seen_header').html(header);
            $('#loading').hide();
            $('#seen_container').show();
        }
    });
}

function appearanceLabel(item){
    var times = '';

    $.each(item.times, function(key, value){
        times = '<div class="row' + (key % 2) + '">' + value + '</div>' + times;
    });

    return `<div>
                <a href="javascript:closeTimes();">Close this tab</a>
            </div>
            <div class="row1">
                <strong>Lat:</strong> ${item.latitude.toFixed(7)}
            </div>
            <div class="row0">
                <strong>Long:</strong> ${item.longitude.toFixed(7)}
            </div>
            <div class="row1">
              <strong>Appearances:</strong> ${item.count.toLocaleString()}
            </div>
            <div class="row0"><strong>Times:</strong></div>
            <div>
                ${times}
            </div>`;
}

function processAppearance(i, item){
    var saw = new Date(item.disappear_time);
    saw =   saw.getHours() + ":" +
            ("0" + saw.getMinutes()).slice(-2) + ":" +
            ("0" + saw.getSeconds()).slice(-2) + " " +
            saw.getDate() + " " +
            monthArray[saw.getMonth()] + " " +
            saw.getFullYear();
    var uuid = item.latitude.toFixed(7) + "_" + item.longitude.toFixed(7);
    if(!((uuid) in map_data.appearances)){
        if (item.marker) item.marker.setMap(null);
          item.count = 1;
          item.times = [saw];
          item.uuid = uuid;
          item.marker = setupPokemonMarker(item, true);

          map_data.appearances[item.uuid] = item;
    }else{
        map_data.appearances[uuid].count++;
        map_data.appearances[uuid].times.push(saw);
    }

    lastappearance = Math.max(lastappearance, item.disappear_time);
}

function updateDetails(){
    loadDetails().done(function (result) {
        $.each(result.appearances, processAppearance)
    });
}

function clearMarkers(){
    $.each(map_data.appearances, function(key, value) {
          map_data.appearances[key].marker.setMap(null);
          delete map_data.appearances[key];
    });
}

function showDetails(id){
    //Only load google maps once, and only if requested
    if(!this.mapLoaded)
        initMap();
    clearMarkers();
    lastappearance = 0;
    pokemonid = id;
    document.getElementById("location_details").style.display = "block";
    detailInterval = window.setInterval(updateDetails, 5000);
    updateDetails();

    return false;
}

function closeOverlay(){
    document.getElementById("location_details").style.display = "none";
    window.clearInterval(detailInterval)
    return false;
}

function addElement(pokemon_id, name){
    jQuery('<div/>', {
        id: 'seen_' + pokemon_id,
        class: 'item'
    }).appendTo('#seen_container');

    jQuery('<div/>',{
        id: 'seen_' + pokemon_id + '_base',
        class: 'container'
    }).appendTo('#seen_' + pokemon_id);

    var imageContainer = jQuery('<div/>',{
                            class: 'image',
                        }).appendTo('#seen_' + pokemon_id + '_base');

    jQuery('<img/>', {
        src: 'static/icons/' + pokemon_id + '.png',
        alt: 'Image for Pokemon #' + pokemon_id
    }).appendTo(imageContainer);

    var baseDetailContainer = jQuery('<div/>', {
                                    class: 'info'
                                }).appendTo('#seen_' + pokemon_id + '_base');

    jQuery('<div/>', {
        id: 'name_' + pokemon_id,
        class: 'name'
    }).appendTo(baseDetailContainer);

    jQuery('<a/>',{
        id: 'link_' + pokemon_id,
        href: 'http://www.pokemon.com/us/pokedex/' + pokemon_id,
        target: '_blank',
        title: 'View in Pokedex',
        text: name
    }).appendTo('#name_' + pokemon_id);

    jQuery('<div/>', {
        id: 'count_' + pokemon_id,
        class: 'seen'
    }).appendTo(baseDetailContainer);

    jQuery('<div/>', {
        id: 'seen_' + pokemon_id + '_details',
        class: 'details',
    }).appendTo('#seen_' + pokemon_id);

    jQuery('<div/>', {
        id: 'lastseen_' + pokemon_id,
        class: 'lastseen'
    }).appendTo('#seen_' + pokemon_id + '_details');

    jQuery('<div/>',{
        id: 'location_' + pokemon_id,
        class: 'location'
    }).appendTo('#seen_' + pokemon_id + '_details');

    jQuery('<a/>',{
        href: 'javascript:showDetails(' + pokemon_id + ');',
        text: 'All Locations'
    }).appendTo('#seen_' + pokemon_id + '_details');
}

function redrawAppearances(appearances){
    $.each(appearances, function(key, value) {
        var item = appearances[key];
        if (!item.hidden) {
          var new_marker = setupPokemonMarker(item, true);
          item.marker.setMap(null);
          appearances[key].marker = new_marker;
        }
    });
}

//Override map.js initMap
function initMap(){
    map = new google.maps.Map(document.getElementById('location_map'), {
        zoom: 16,
        center: {lat: center_lat, lng: center_lng},
        fullscreenControl: false,
        streetViewControl: false,
        mapTypeControl: true,
        mapTypeControlOptions: {
          style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
          position: google.maps.ControlPosition.RIGHT_TOP,
          mapTypeIds: [
            google.maps.MapTypeId.ROADMAP,
            google.maps.MapTypeId.SATELLITE,
            'nolabels_style',
            'dark_style',
            'style_light2',
            'style_pgo',
            'dark_style_nl',
            'style_light2_nl',
            'style_pgo_nl'
          ]
        }
  });

  this.mapLoaded = true;

  google.maps.event.addListener(map, 'zoom_changed', function() {
    redrawAppearances(map_data.appearances);
  });
}

updateMap();