
 ///////////////
 // basic map //
 ///////////////

"use strict";


let search_address = $("#propertymap").val();
let search_address_json = search_address.replace(/'/g, '"');
console.log(search_address_json);
let info = JSON.parse(search_address_json);
let latitude = parseFloat(info.latitude);
let longitude = parseFloat(info.longitude);

console.log(latitude,longitude);

 // });

let eastAustralia = {lat: latitude, lng:longitude};

let map = new google.maps.Map(document.querySelector('#map'), {
	center: eastAustralia,
	zoom: 8,
// Note: the following are marked the opposite of the default setting
// (that is, they're marked "false" if they're true by
// default, and "true" if they're false by default) so that
// uncommenting the following lines will actually change the map

// mapTypeControl: false,
// zoomControl: false,
// scaleControl: true,
// streetViewControl: false,
// rotateControl: true, // only available for locations with 45° imagery
// fullscreenControl: true

});

////////////
// marker //
////////////

function addMarker() {
  let icon = {
    url: 'http://remaxbeitshemesh.com/wp-content/themes/realty/lib/images/map-marker/map-marker-red-fat.png',
    scaledSize: new google.maps.Size(18,30)
    }
  let nearSydney = new google.maps.LatLng(latitude, longitude);
  let marker = new google.maps.Marker({
      position: nearSydney,
      map: map,
      title: 'Hover text',
      icon: icon
  });
  return marker;
}

let marker = addMarker();

///////////////
//info window //
///////////////

function addInfoWindow() {

  let contentString = '<div id="content">' +
    '<h1>All my custom content</h1>' +
    '</div>';

  let infoWindow = new google.maps.InfoWindow({
    content: contentString,
    maxWidth: 200
  });

  marker.addListener('click', function() {
    infoWindow.open(map, marker);
  });
}

// addInfoWindow()


////////////
// styles //
////////////

function addStyles() {

  let styles = [
  {
      "featureType": "water",
      "stylers": [
        { "color": "#2529da" }
      ]
    }
  ];

  let styledMapOptions = {
      name: 'Custom Style'
  };

  let customMapType = new google.maps.StyledMapType(
          styles,
          styledMapOptions);

  map.mapTypes.set('map_style', customMapType);
  map.setMapTypeId('map_style');

}

// addStyles();

//////////////////////////
// geocoding by address //
//////////////////////////

function addHackbrightByAddress() {
  let hackbright = new google.maps.Geocoder();
  let address = "683 Sutter Street, San Francisco, CA";

  hackbright.geocode({'address': address},
    function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        let marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
        });
      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
  });
}

// addHackbrightByAddress();

/////////////////////////////
// geocoding by place name //
/////////////////////////////

function addGoldenGateBridgeByName() {

  let beautifulBridge = new google.maps.Geocoder();
  let premise = "Golden Gate Bridge";

  beautifulBridge.geocode({'address': premise}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);

        let marker = new google.maps.Marker({
          map: map,
          place: {
            location: results[0].geometry.location,
            query: "Golden Gate"
          }
        });
        // Construct a new InfoWindow.
        let infoWindow = new google.maps.InfoWindow({
          content: 'Golden Gate Bridge'
        });

        // Opens the InfoWindow when marker is clicked.
        marker.addListener('click', function() {
          infoWindow.open(map, marker);
        });
      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
    });
}

// addGoldenGateBridgeByName();

///////////////
// polyLines //
///////////////

function addTripPath() {
  let sydney = {lat: -33.8675, lng: 151.2070};
  let bathurst = {lat: -33.4177, lng: 149.5810};
  let canberra = {lat: -35.2820, lng: 149.1287};

  let roadTripStops = [
      sydney,
      bathurst,
      canberra
  ];

  let tripPath = new google.maps.Polyline({
      path: roadTripStops,
      geodesic: true,
      strokeColor: '#ff0000',
      strokeOpacity: 1.0,
      strokeWeight: 5
  });

  tripPath.setMap(map);
}

// addTripPath();

////////////////
// directions //
////////////////

function displayDirections() {

  let sydney = {lat: -33.8675, lng: 151.2070};
  let bathurst = {lat: -33.4177, lng: 149.5810};
  let canberra = {lat: -35.2820, lng: 149.1287};

  let bathurstWaypoint = {
          location: bathurst,
          stopover: true
  };

  let routeOptions = {
      origin: sydney,
      destination: canberra,
      waypoints: [bathurstWaypoint],
      travelMode: google.maps.TravelMode.DRIVING
    };

  let directionsService = new google.maps.DirectionsService;
  directionsService.route(routeOptions, function(response, status) {
      if (status === google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });

  let directionsDisplay = new google.maps.DirectionsRenderer;
  directionsDisplay.setMap(map);
}

// displayDirections();
