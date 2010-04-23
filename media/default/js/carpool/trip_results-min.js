
var trip=new Array();var trip_pls;var departure_poly;var arrival_poly;var current_step;var trip_pg=10;var trip_offers_updater=new TripUpdater(trip_pg,TYPE_OFFER,false);var trip_demands_updater=new TripUpdater(trip_pg,TYPE_DEMAND,false);completeDragMarker=function(marker,pixel){if(marker){step_idx=parseInt(marker.attributes.id,10);if(step_idx>=0){removeTrip();trip[step_idx].linestring=null;if(step_idx!=trip.length-1){trip[step_idx+1].linestring=null;}
current_step=1;}
updateTrip();displayDepartureRadiusCircle();displayArrivalRadiusCircle();retrieveTrips();}}
function displayTrip(){var linestring_array=new Array();for(var index=0,len=trip.length;index<len;index++){var step=trip[index];if(step.marker){if(getTripType()!=TYPE_DEMAND||getTripType()==TYPE_DEMAND&&(index==0||index==len-1)){markers.addFeatures([step.marker]);}}
if(step.linestring){linestring_array[linestring_array.length]=step.linestring;}}
if(getTripType()!=TYPE_DEMAND&&linestring_array.length>0){trip_pls=new OpenLayers.Feature.Vector(new OpenLayers.Geometry.MultiLineString(linestring_array),null,route_style)
trip_layer.addFeatures([trip_pls]);if(isRouteOK()){calculateSimpleTripBuffer(trip_pls,map,trip_offer_radius,null,trip_layer);}}}
function removeTrip(){for(var index=0,len=trip.length;index<len;index++){var step=trip[index];if(step.marker){hideMarkerPopup(step.marker);markers.removeFeatures([step.marker]);}}
if(trip_pls){trip_layer.removeFeatures([trip_pls]);trip_pls=null;}
if(simple_trip_buffer){trip_layer.removeFeatures([simple_trip_buffer]);simple_trip_buffer=null;}}
function displayDepartureRadiusCircle(){removeDepartureRadiusCircle();if(getTripType()==TYPE_OFFER)
return;if(trip[0].marker){departure_poly=new OpenLayers.Feature.Vector(getCircle(trip[0].marker.geometry,trip_demand_radius),null,buffer_style);trip_layer.addFeatures([departure_poly]);}}
function removeDepartureRadiusCircle(){if(departure_poly){trip_layer.removeFeatures([departure_poly]);departure_poly=null;}}
function displayArrivalRadiusCircle(){removeArrivalRadiusCircle();if(getTripType()==TYPE_OFFER)
return;if(trip[trip.length-1].marker){arrival_poly=new OpenLayers.Feature.Vector(getCircle(trip[trip.length-1].marker.geometry,trip_demand_radius),null,buffer_style);trip_layer.addFeatures([arrival_poly]);}}
function removeArrivalRadiusCircle(){if(arrival_poly){trip_layer.removeFeatures([arrival_poly]);arrival_poly=null;}}
function updateTrip(){for(var index=current_step,len=trip.length;index<len;index++){current_step=index;if(getTripType()!=TYPE_DEMAND&&trip[index].linestring==null&&trip[index-1].marker&&trip[index].marker){setDirections(OpenLayers.Layer.SphericalMercator.inverseMercator(trip[index-1].marker.geometry.x,trip[index-1].marker.geometry.y),OpenLayers.Layer.SphericalMercator.inverseMercator(trip[index].marker.geometry.x,trip[index].marker.geometry.y));return;}}
current_step+=1;if(current_step>=trip.length){displayTrip();}}
function retrieveTrips(){if(getTripType()==TYPE_DEMAND||trip_pls!=null){if(!isRouteOK())return;displayWaitForResults();new Ajax.Request('/ajax/get_trips/'+trip_id+'/',{method:'post',parameters:{geometry:(getTripType()!=TYPE_DEMAND)?wkt.write(new OpenLayers.Feature.Vector(trip_pls.geometry)):"",departure_point:wkt.write(trip[0].marker),arrival_point:wkt.write(trip[trip.length-1].marker),interval_min_radius:7-interval_min_radius,interval_max_radius:interval_max_radius,offer_radius:(getTripType()!=TYPE_DEMAND)?trip_offer_radius:0,demand_radius:(getTripType()!=TYPE_OFFER)?trip_demand_radius:0},onSuccess:function(transport){var json=transport.responseText.evalJSON();hideWaitForResults();if(getTripType()!=TYPE_DEMAND)
trip_demands_updater.updateTrips(json.trip_demands,json.authenticated);if(getTripType()!=TYPE_OFFER)
trip_offers_updater.updateTrips(json.trip_offers,json.authenticated);},onFailure:function(){hideWaitForResults();}});}else{setTimeout("retrieveTrips()",100);}}
function displayWaitForResults(){$('wait').show();}
function hideWaitForResults(){$('wait').hide();}
function setDirections(from,to){$('wait').show();gdir.load("from: "+from.lat+", "+from.lon+" to: "+to.lat+", "+to.lon,{getPolyline:true});}
function handleErrors(){$('wait').hide();if(gdir.getStatus().code==G_GEO_UNKNOWN_ADDRESS){alert(gettext('Error : Address not found.'));}else if(gdir.getStatus().code==G_GEO_UNKNOWN_DIRECTIONS){first_point=(current_step-1==0)?trip[0].city:interpolate(gettext('Check point n&deg;%s'),[current_step-1]);second_point=(current_step==trip.length-1)?trip[trip.length-1].city:interpolate(gettext('Check point n&deg;%s'),[current_step]);alert(interpolate(gettext('Route %s - %s not found.'),[first_point,second_point]));}else if(gdir.getStatus().code==G_GEO_SERVER_ERROR){alert(interpolate(gettext('Directions request could not be successfully processed.\nError code: %s'),[gdir.getStatus().code]));}else if(gdir.getStatus().code==G_GEO_BAD_KEY){alert(interpolate(gettext('Invalid key.\nError code: %s'),[gdir.getStatus().code]));}else if(gdir.getStatus().code==G_GEO_BAD_REQUEST){alert(interpolate(gettext('A directions request could not be successfully parsed.\nError code: %s'),[gdir.getStatus().code]));}else{alert(interpolate(gettext('An error occurs.\nError code: %s'),[gdir.getStatus().code]));}
current_step+=1;updateTrip();}
function onGDirectionsLoad(){$('wait').hide();var points=new Array();var lonlat;for(var i=0;i<gdir.getPolyline().getVertexCount();i++){lonlat=OpenLayers.Layer.SphericalMercator.forwardMercator(gdir.getPolyline().getVertex(i).lng(),gdir.getPolyline().getVertex(i).lat());points[points.length]=new OpenLayers.Geometry.Point(lonlat.lon,lonlat.lat);}
if(points.length==1){points[points.length]=points[0];}
trip[current_step].linestring=new OpenLayers.Geometry.LineString(points);updateTrip();}
function isRouteOK(){if(getTripType()==TYPE_DEMAND)return true;for(var index=1,len=trip.length;index<len;++index){if(trip[index].linestring==null)return false;}
return true;}
function getTripType(){return trip_type;}
function isRegular(){return trip_regular;}
if(getTripType()!=TYPE_DEMAND){onSlideOfferRadius=function(v){var value=v/1000+' km';$('verbose_offer_radius').innerHTML=value;}
onChangeOfferRadius=function(v){onSlideOfferRadius(v);removeTrip();trip_offer_radius=(v==0)?500:v;displayTrip();retrieveTrips();}
var slider_offer=new Control.Slider('handle_offer_radius','track_offer_radius',{range:$R(0,20000),values:[0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000],increment:1000,sliderValue:(trip_offer_radius==500)?0:trip_offer_radius,onSlide:onSlideOfferRadius,onChange:onChangeOfferRadius});observeRadiusLeft('slider_offer_left',slider_offer);observeRadiusRight('slider_offer_right',slider_offer);}
if(getTripType()!=TYPE_OFFER){onSlideDemandRadius=function(v){var value=v/1000+' km';$('verbose_demand_radius').innerHTML=value;}
onChangeDemandRadius=function(v){onSlideDemandRadius(v);trip_demand_radius=(v==0)?500:v;displayDepartureRadiusCircle();displayArrivalRadiusCircle();retrieveTrips();}
var slider_demand=new Control.Slider('handle_demand_radius','track_demand_radius',{range:$R(0,20000),values:[0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000],sliderValue:(trip_demand_radius==500)?0:trip_demand_radius,increment:1000,onSlide:onSlideDemandRadius,onChange:onChangeDemandRadius});observeRadiusLeft('slider_demand_left',slider_demand);observeRadiusRight('slider_demand_right',slider_demand);}
if(!isRegular()){onSlideIntervalMinRadius=function(v){$('verbose_interval_min_radius').innerHTML=((v==7)?"-":"")+(v-7)+'j';}
onChangeIntervalMinRadius=function(v){onSlideIntervalMinRadius(v);interval_min_radius=v;retrieveTrips();}
var slider_interval_min=new Control.Slider('handle_interval_min_radius','track_interval_min_radius',{range:$R(0,7),values:[0,1,2,3,4,5,6,7],sliderValue:interval_min_radius,onSlide:onSlideIntervalMinRadius,onChange:onChangeIntervalMinRadius});observeRadiusLeft('slider_interval_min_left',slider_interval_min);observeRadiusRight('slider_interval_min_right',slider_interval_min);onSlideIntervalMaxRadius=function(v){$('verbose_interval_max_radius').innerHTML='+'+v+'j';}
onChangeIntervalMaxRadius=function(v){onSlideIntervalMaxRadius(v);interval_max_radius=v;retrieveTrips();}
var slider_interval_max=new Control.Slider('handle_interval_max_radius','track_interval_max_radius',{range:$R(0,7),values:[0,1,2,3,4,5,6,7],sliderValue:interval_max_radius,onSlide:onSlideIntervalMaxRadius,onChange:onChangeIntervalMaxRadius});observeRadiusLeft('slider_interval_max_left',slider_interval_max);observeRadiusRight('slider_interval_max_right',slider_interval_max);}
if($('help_permalink'))
new Tip($('help_permalink'),help_permalink_tt);if($('help_slider_date'))
new Tip($('help_slider_date'),help_slider_date_tt);if($('help_slider_radius_driver'))
new Tip($('help_slider_radius_driver'),help_slider_radius_driver_tt);if($('help_slider_radius_passenger'))
new Tip($('help_slider_radius_passenger'),help_slider_radius_passenger_tt);Event.observe(window,'load',function(){initOL();retrieveTrips();});$('permalink_field').observe('click',function(){$('permalink_field').select();});if(getTripType()==TYPE_BOTH){$('res_o').observe('click',function(){Element.extend($('res_o'));Element.extend($('res_d'));$('trip_list_content_d').hide();$('trip_pages_d').hide();$('res_d').removeClassName('current');$('trip_list_content_o').show();$('trip_pages_o').show();$('res_o').addClassName('current');});$('res_d').observe('click',function(){Element.extend($('res_o'));Element.extend($('res_d'));$('trip_list_content_o').hide();$('trip_pages_o').hide();$('res_o').removeClassName('current');$('trip_list_content_d').show();$('trip_pages_d').show();$('res_d').addClassName('current');});}
if($('form_save_trip')){$('form_save_trip').observe('submit',function(event){var departure;var arrival;var steps=new Array();for(var index=0,len=trip.length;index<len;++index){var step=$H({'point':wkt.write(trip[index].marker)});if(index==0){departure=step;}else if(index==len-1){arrival=step;}else if(getTripType()!=TYPE_DEMAND){steps[steps.length]=step;}}
var trip_details=$H({'departure':departure,'arrival':arrival,'interval_min_radius':7-interval_min_radius,'interval_max_radius':interval_max_radius});if(getTripType()!=TYPE_OFFER){trip_details.set('demand_radius',trip_demand_radius);}
if(getTripType()!=TYPE_DEMAND){trip_details.set('route',wkt.write(trip_pls));trip_details.set('steps',steps);trip_details.set('offer_radius',trip_offer_radius);}
$('trip_details').setValue(trip_details.toJSON());});}