var trip_pls;

function displayDepartureRadiusCircle(geom, radius) {
    var departure_poly = new OpenLayers.Feature.Vector(getCircle(geom.geometry, radius), null, buffer_style);
    trip_layer.addFeatures([departure_poly]);
}

function displayArrivalRadiusCircle(geom, radius) {
    var arrival_poly = new OpenLayers.Feature.Vector(getCircle(geom.geometry, radius), null, buffer_style);
    trip_layer.addFeatures([arrival_poly]);
}
/************************* EVENTS ****************************/
// Load OL
Event.observe(window, 'load', function() {
    initOL();
});
