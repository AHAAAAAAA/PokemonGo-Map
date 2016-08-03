/*Shared*/
var monthArray = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/*Main stats page*/
var rawDataIsLoading = false;
var totalPokemon = 151;

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
        id: 'seen_' + pokemon_id + '_details',
        class: 'details',
    }).appendTo('#seen_' + pokemon_id);

    jQuery('<div/>', {
        id: 'count_' + pokemon_id,
        class: 'seen'
    }).appendTo('#seen_' + pokemon_id + '_details');

    jQuery('<div/>', {
        id: 'lastseen_' + pokemon_id,
        class: 'lastseen'
    }).appendTo('#seen_' + pokemon_id + '_details');

    jQuery('<div/>',{
        id: 'location_' + pokemon_id,
        class: 'location'
    }).appendTo('#seen_' + pokemon_id + '_details');

    jQuery('<a/>',{
        href: 'javascript:showOverlay(' + pokemon_id + ');',
        text: 'All Locations'
    }).appendTo('#seen_' + pokemon_id + '_details');
}

function processSeen(seen){
    var total = seen.total;
    var shown = Array();

    seen.pokemon.sort(function(a, b){
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

    for(var i = seen.pokemon.length - 1; i >= 0; i--){
        var item = seen.pokemon[i];
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
        $('#count_' + item.pokemon_id).html('<strong>Seen:</strong> ' + item.count.toLocaleString() + ' (' + percentage + '%)');
        $('#lastseen_' + item.pokemon_id).html('<strong>Last Seen:</strong> ' + lastSeen);
        $('#location_' + item.pokemon_id).html('<strong>Location:</strong> ' + location);
        $('#seen_' + item.pokemon_id).show();
        //Reverting to classic javascript here as it's supposed to increase performance
        document.getElementById('seen_container').insertBefore(document.getElementById('seen_' + item.pokemon_id), document.getElementById('seen_container').childNodes[0]);
        shown.push(item.pokemon_id);
    }

    //Hide any unneeded items
    for(var i = 1; i <= totalPokemon; i++){
        if(shown.indexOf(i) < 0)
            $('#seen_' + i).hide();
    }

    document.getElementById("seen_total").innerHTML = 'Total: ' + total.toLocaleString();
}

//Override UpdateMap in map.js to take advantage of a pre-existing interval.
function updateMap(firstRun){
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

updateMap();

/*Overlay*/
var detailsLoading = false;
var detailInterval = null;
var lastappearance = 1;
var pokemonid = 0;
var mapLoaded = false;
var detailsPersist = false;
var map = null;
var heatmap = null;
var heatmap_numPoints = -1;
var heatmapPoints = [];
map_data.appearances = {};

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
    var uuid = marker.position.lat().toFixed(7) + "_" + marker.position.lng().toFixed(7);
    $('#times_list').html(appearanceTab(map_data.appearances[uuid]));
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

  var style_NoLabels = new google.maps.StyledMapType(noLabelsStyle, {
    name: "No Labels"
  });
  map.mapTypes.set('nolabels_style', style_NoLabels);

  var style_dark = new google.maps.StyledMapType(darkStyle, {
    name: "Dark"
  });
  map.mapTypes.set('dark_style', style_dark);

  var style_light2 = new google.maps.StyledMapType(light2Style, {
    name: "Light2"
  });
  map.mapTypes.set('style_light2', style_light2);

  var style_pgo = new google.maps.StyledMapType(pGoStyle, {
    name: "PokemonGo"
  });
  map.mapTypes.set('style_pgo', style_pgo);

  var style_dark_nl = new google.maps.StyledMapType(darkStyleNoLabels, {
    name: "Dark (No Labels)"
  });
  map.mapTypes.set('dark_style_nl', style_dark_nl);

  var style_light2_nl = new google.maps.StyledMapType(light2StyleNoLabels, {
    name: "Light2 (No Labels)"
  });
  map.mapTypes.set('style_light2_nl', style_light2_nl);

  var style_pgo_nl = new google.maps.StyledMapType(pGoStyleNoLabels, {
    name: "PokemonGo (No Labels)"
  });
  map.mapTypes.set('style_pgo_nl', style_pgo_nl);

  map.addListener('maptypeid_changed', function(s) {
    Store.set('map_style', this.mapTypeId);
  });

  map.setMapTypeId(Store.get('map_style'));
  google.maps.event.addListener(map, 'idle', updateMap);

  mapLoaded = true;

  google.maps.event.addListener(map, 'zoom_changed', function() {
    redrawAppearances(map_data.appearances);
  });
}

function resetMap(){
    $.each(map_data.appearances, function(key, value) {
          map_data.appearances[key].marker.setMap(null);
          delete map_data.appearances[key];
    });

    heatmapPoints = [];
    heatmap_numPoints = 0;
    if(heatmap){
        heatmap.setMap(null);
    }

    lastappearance = 0;
}

function showOverlay(id){
    //Only load google maps once, and only if requested
    if(!mapLoaded)
        initMap();
    resetMap();
    pokemonid = id;
    $('#location_details').show();
    location.hash = 'overlay_' + pokemonid;
    updateDetails();
    detailInterval = window.setInterval(updateDetails, 5000);

    return false;
}

function closeOverlay(){
    $('#location_details').hide();
    window.clearInterval(detailInterval);
    closeTimes();
    location.hash = '';
    return false;
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

    heatmapPoints.push(new google.maps.LatLng(item.latitude, item.longitude));
    lastappearance = Math.max(lastappearance, item.disappear_time);
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

function appearanceTab(item){
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

function updateDetails(){
    loadDetails().done(function (result) {
        $.each(result.appearances, processAppearance);

        //Redraw the heatmap with all the new appearances
        if(heatmap_numPoints != heatmapPoints.length){
            if(heatmap){
                heatmap.setMap(null);
            }
            heatmap = new google.maps.visualization.HeatmapLayer({
                                data: heatmapPoints,
                                map: map,
                                radius: 50
                            });
            heatmap_numPoints = heatmapPoints.length;
        }
    });
}

if(location.href.match(/overlay_[0-9]+/g))
    showOverlay(location.href.replace(/^.*overlay_([0-9]+).*$/, '$1'));