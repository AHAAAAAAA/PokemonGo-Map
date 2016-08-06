/*eslint no-unused-vars: ["error", { "varsIgnorePattern": "initMap" }]*/
/*global google */
/*global centerLat */
/*global centerLng */
/*global $ */

var map
var markers = {}
var circles = {}
var gMarkerid = 0

function initMap () {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {
      lat: centerLat,
      lng: centerLng
    },
    zoom: 16,
    fullscreenControl: true,
    streetViewControl: false,
    mapTypeControl: false,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
      position: google.maps.ControlPosition.RIGHT_TOP,
      mapTypeIds: [
        google.maps.MapTypeId.ROADMAP,
        google.maps.MapTypeId.SATELLITE
      ]
    }
  })

  google.maps.event.addListener(map, 'click', function (event) {
    gMarkerid++
    markers[gMarkerid] = placeMarker(event.latLng, gMarkerid)
  })
}

function placeMarker (location, markerid) {
  var marker = new google.maps.Marker({
    position: location,
    map: map,
    draggable: true,
    clickable: true
  })
  marker.addListener('drag', function () { clearCircles(markerid) })
  marker.addListener('dragend', function (event) { genCircles(event.latLng, 5, markerid) })
  genCircles(location, 5, markerid)
  return marker
}

function genCircles (location, steps, markerid) {
  $.ajax({
    url: 'beehive-calc',
    type: 'GET',
    data: {
      'lat': location.lat(),
      'lng': location.lng(),
      'steps': steps,
      'markerid': markerid
    },
    dataType: 'json',
    cache: false
  }).done(function (result) {
    var circleSet = []
    $.each(result.steps, function (index, value) {
      circleSet.push(setupScannedMarker(value[0], value[1]))
    })
    circles[result.markerid] = circleSet
  })
}

function clearCircles (markerid) {
  $.each(circles[markerid], function (index, value) {
    value.setMap(null)
  })
}

function setupScannedMarker (lat, lng) {
  var marker = new google.maps.Circle({
    map: map,
    clickable: false,
    center: new google.maps.LatLng(lat, lng),
    radius: 70,
    fillColor: '#cccccc',
    strokeWeight: 1
  })
  return marker
}
