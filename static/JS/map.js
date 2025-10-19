
let map = L.map('map').setView([57.04708, 9.924603], 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let popup = L.popup();

function on_map_click(e) {
    popup
        .setLatLng(e.latlng)
        .setContent('You clicked the map at ' + e.latlng.toString())
        .openOn(map);
}
map.on('click', on_map_click);


function clear_map() {
    map.eachLayer(function (layer) {
        if (!!layer.toGeoJSON) {
            map.removeLayer(layer);
        }
    });
}

function plot_to_map(data, color) {
    const line = L.polyline(data, { color, weight: 2 }).addTo(map);
    L.polylineDecorator(line, {
        patterns: [{
            offset: '0',
            repeat: '100km',
            symbol: L.Symbol.arrowHead({
              pixelSize: 10,
              headAngle: 65,        // sharper angle
              polygon: false,       // stroke only → “>” angle
              pathOptions: { color, weight: 2, opacity: 1 }
            })
          }]
    }).addTo(map);
}




