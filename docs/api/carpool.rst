Carpool Trips 
==============

The API provides the following URIs to interact with trip data

List
----

Retreive the list of existing trips, with the complete description of each item. 

**URL**
    /trips/
*Verb*
    GET
*Data*
    None
    
Example::

    $ curl -X GET http://api.bisonvert.net/trips/ -d 'trip_type=offer&departure_city=paris&arrival_city=toulouse'
    [
    {
        "dows": [], 
        "offer": {
            "driver_km_price": "20.00", 
            "driver_pets_accepted": true, 
            "direction_route": "LINESTRING (...)", 
            "driver_seats_available": null, 
            "radius": 500, 
            "checkpoints": "(lp1\n.", 
            "driver_smokers_accepted": null, 
            "driver_place_for_luggage": null
        }, 
        "departure_point": "POINT (1.8149983000000001 43.6988774000000078)", 
        "time": null, 
        "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
        "interval_min": 7, 
        "arrival_address": "", 
        "interval_max": 0, 
        "regular": false, 
        "departure_city": "Lavaur (81)", 
        "user": {
            "username": "alexis", 
            "id": 1
        }, 
        "demand": null, 
        "date": "2010-01-20", 
        "departure_address": "", 
        "id": 27, 
        "arrival_city": "paris"
    }, 
    {
        "dows": [], 
        "departure_point": "POINT (1.4429513000000000 43.6043630000000135)", 
        "time": "08:00:00", 
        "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
        "interval_min": 7, 
        "arrival_address": "", 
        "interval_max": 0, 
        "regular": false, 
        "departure_city": "toulouse", 
        "user": {
            "username": "alexis", 
            "id": 1
        }, 
        "demand": {
            "passenger_max_km_price": null, 
            "passenger_smokers_accepted": true, 
            "passenger_min_remaining_seats": null, 
            "passenger_car_type_id": null, 
            "radius": 500, 
            "passenger_place_for_luggage": false, 
            "passenger_pets_accepted": true, 
            "id": 43
        }, 
        "date": "2010-01-20", 
        "departure_address": "", 
        "id": 32, 
        "arrival_city": "paris"
    }, 
    {
        "dows": [], 
        "departure_point": "POINT (1.4429513000000000 43.6043630000000135)", 
        "time": "09:00:00", 
        "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
        "interval_min": 7, 
        "arrival_address": "", 
        "interval_max": 0, 
        "regular": false, 
        "departure_city": "toulouse", 
        "user": {
            "username": "alexis", 
            "id": 1
        }, 
        "demand": {
            "passenger_max_km_price": null, 
            "passenger_smokers_accepted": true, 
            "passenger_min_remaining_seats": null, 
            "passenger_car_type_id": null, 
            "radius": 15000, 
            "passenger_place_for_luggage": false, 
            "passenger_pets_accepted": true, 
            "id": 39
        }, 
        "date": "2010-01-24", 
        "departure_address": "", 
        "id": 28, 
        "arrival_city": "paris"
    }
    ]


Get
---

Retreive informations about a specific trip, by specifying it's id.

**URL**
    /trips/id
*Verb*
    GET
*Data*
    None

Exemple::
    
    $ curl -X GET http://api.bisonvert.net/trips/35/
    {
        "dows": [], 
        "departure_point": "POINT (1.4429513000000000 43.6043630000000135)", 
        "time": "08:00:00", 
        "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
        "interval_min": 7, 
        "arrival_address": "", 
        "interval_max": 0, 
        "regular": false, 
        "departure_city": "toulouse", 
        "user": {
            "username": "alexis", 
            "id": 1
        }, 
        "demand": {
            "passenger_max_km_price": null, 
            "passenger_smokers_accepted": true, 
            "passenger_min_remaining_seats": null, 
            "passenger_car_type_id": null, 
            "radius": 500, 
            "passenger_place_for_luggage": false, 
            "passenger_pets_accepted": true, 
            "id": 46
        }, 
        "date": "2010-01-20", 
        "departure_address": "", 
        "id": 35, 
        "arrival_city": "paris"
    }

Search
------
It's possible to search the results by specifying some parameters. The search
always return a dict with tree keys: trip demands, trip offers and trip object,
if there is one.

**URL**
    /trips/search/:id
    /trips/search/
*Verb*
    GET
*Data*
    * `trip_id`: the trip id to find matches on. If specified, other informations aren't needed.
    * `is_offer`: if specified, search for passengers (trip demands).
    * `is_demand`: if specified, search for drivers (trip offers).
    * `offer_radius`: the offer radius, in meters.
    * demand_radius`: the demand radius, in meters.
    * `date: the date` of the trip, in the form YYYY-MM-DD.
    * `interval_min`: number of days to seek before the given date.
    * `interval_max`: number of days to seek after the given date.
    * `is_regular`: is the trip a regular one ? if so, please specify the "dows" parameter
    * `dows`: day of weeks
    * `route`: WKT Multipoint route.
    * `departure_point`: departure WKT point
    * `arrival_point`: arrival WKT point
    
Parameters can be just the id of a already registred trip, or a list of values::

    $ curl -X GET http://api.bisonvert.net/trips/search/27/
    {
        "trip_demands": [
            {
                "dows": [], 
                "departure_point": "POINT (1.4429513000000000 43.6043630000000135)", 
                "time": "09:00:00", 
                "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
                "interval_min": 0, 
                "arrival_address": "", 
                "interval_max": 0, 
                "regular": false, 
                "departure_city": "toulouse", 
                "user": {
                    "username": "test", 
                    "id": 5
                }, 
                "demand": {
                    "passenger_max_km_price": null, 
                    "passenger_smokers_accepted": true, 
                    "passenger_min_remaining_seats": null, 
                    "passenger_car_type_id": null, 
                    "radius": 15000, 
                    "passenger_place_for_luggage": false, 
                    "passenger_pets_accepted": true, 
                    "id": 39
                }, 
                "date": "2010-01-20", 
                "departure_address": "", 
                "id": 28, 
                "arrival_city": "paris"
            }
        ], 
        "trip_offers": null, 
        "trip": {
            "dows": [], 
            "offer": {
                "driver_km_price": "20.00", 
                "driver_pets_accepted": true, 
                "direction_route": "LINESTRING (...)", 
                "driver_seats_available": null, 
                "radius": 500, 
                "checkpoints": "(lp1\n.", 
                "driver_smokers_accepted": null, 
                "driver_place_for_luggage": null
            }, 
            "departure_point": "POINT (1.8149983000000001 43.6988774000000078)", 
            "time": null, 
            "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
            "interval_min": 7, 
            "arrival_address": "", 
            "interval_max": 0, 
            "regular": false, 
            "departure_city": "Lavaur (81)", 
            "user": {
                "username": "test", 
                "id": 5
            }, 
            "demand": null, 
            "date": "2010-01-20", 
            "departure_address": "", 
            "id": 27, 
            "arrival_city": "paris"
        }
    }
    
Or to make a search by specifying the values directly to the API::

    $ curl -X GET "http://api.bisonvert.net/trips/search/?is_demand=true&arrival_point=POINT+(2.3333330000000001+48.8666669999999996)&departure_point=POINT+(1.4333330000000000+43.6000000000000014)&demand_radius=20000&date=2020-01-20"
    {
    "trip_demands": null, 
    "trip_offers": [
        {
            "dows": [], 
            "offer": {
                "driver_km_price": "20.00", 
                "driver_pets_accepted": true, 
                "direction_route": "LINESTRING (...)", 
                "driver_seats_available": null, 
                "radius": 500, 
                "checkpoints": "(lp1\n.", 
                "driver_smokers_accepted": null, 
                "driver_place_for_luggage": null
            }, 
            "departure_point": "POINT (1.8149983000000001 43.6988774000000078)", 
            "time": null, 
            "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
            "interval_min": 7, 
            "arrival_address": "", 
            "interval_max": 0, 
            "regular": false, 
            "departure_city": "Lavaur (81)", 
            "user": {
                "username": "test", 
                "id": 5
            }, 
            "demand": null, 
            "date": "2020-01-20", 
            "departure_address": "", 
            "id": 27, 
            "arrival_city": "paris"
        }
    ], 
    "trip": null
    }


New
---

**URL**
    /trips/
*Verb*
    POST
*Data*
    * `departure_city`: the trip departure city  (*required*)
    * `departure_address`: the trip departure adress
    * `departure_point`: the departure geographical point for the trip (*required*)
    * `arrival_city`: the trip arrival city
    * `arrival_address`: the trip arrival adress (*required*)
    * `arrival_point`: the arrival geographical point for the trip (*required*)
    * `regular`: Is the trip a regular one ? True = Yes (*required*)
    * `date`: the date of the trip (*required*)
    * `interval_min`: nomber of interval (days) accepted before the departure date
    * `interval_max`: nomber of interval (days) accepted after the departure date
    * `dows`: if the trip i a regular one, dows contains a Json array containing days of weeks. (*required if the trip is regular*)
    * `comment`: an optionnal comment for this trip
    * `demand`: True or False
    * `offer`: True or False
    * `demand_radius`: perimeter of the passenger search
    * `demand_smokers_accepted`: weather the passenger accepts smokers or not
    * `demand_pets_accepted`: weather the passenger accepts pets or not
    * `demand_place_for_luggage`:  weather the passenger need place for laggages or not
    * `demand_car_type`: the car type id asked by the passenger
    * `demand_min_remaining_seats`:  the number of remaining seats for the passenger
    * `demand_max_km_price`: Maximum price per KM
    * `offer_radius`: perimeter of the conductor search
    * `offer_checkpoints`: checkpoints of the offer trip
    * `offer_route`: SIG route
    * `offer_km_price`: Price per KM asked by the driver
    * `offer_radius`: perimeter of the passenger search
    * `offer_smokers_accepted`: weather the passenger accepts smokers or not
    * `offer_pets_accepted`: weather the passenger accepts pets or not
    * `offer_place_for_luggage`:  weather the driver have place for laggages or not
    * `offer_car_type`: the car type the driver have
    * `offer_seats_available`:  the number of remaining seats for the driver
    * `tag`: a free to use tag. If specified, all trip must have it    

Create a new trip. It can be an offer, a demand or both. the request return a 
item with the complete list of fields. **require to be authenticated**

At least one of 'offer' or 'demand' type are mendatory::
    
    $ curl -X POST http://api.bisonvert.net/trips/ -d 'alert=on&arrival_city=paris&arrival_point=POINT(2.3509871 48.85666670000002)&comment=&date=20/01/2010&demand-passenger_car_type=&demand-passenger_max_km_price=&demand-passenger_min_remaining_seats=&demand-passenger_pets_accepted=on&demand-passenger_smokers_accepted=on&demand-radius=500&departure_address=&departure_city=toulouse&departure_point=POINT(1.4429513 43.60436300000001)&interval_max=0&interval_min=7&name=announce name&offer-radius=500&regular=False&time=8&trip_type=1'
    {
        "dows": [], 
        "departure_point": "POINT (1.4429513000000000 43.6043630000000135)", 
        "time": "08:00:00", 
        "arrival_point": "POINT (2.3509871000000002 48.8566667000000194)", 
        "interval_min": 7, 
        "arrival_address": "", 
        "interval_max": 0, 
        "regular": false, 
        "departure_city": "toulouse", 
        "user": {
            "username": "alexis", 
            "id": 1
        }, 
        "demand": {
            "passenger_max_km_price": null, 
            "passenger_smokers_accepted": true, 
            "passenger_min_remaining_seats": null, 
            "passenger_car_type_id": null, 
            "radius": 500, 
            "passenger_place_for_luggage": false, 
            "_passenger_car_type_cache": null, 
            "passenger_pets_accepted": true, 
            "id": 48
        }, 
        "date": "2010-01-20", 
        "departure_address": "", 
        "id": 37, 
        "arrival_city": "paris"
    }


Edit / Modify
-------------

Edit an existing trip object.

**URL**
    /trips/id
*Verb*
    POST
*Data*
    * `departure_city`: the trip departure city
    * `departure_address`: the trip departure adress
    * `departure_point`: the departure geographical point for the trip 
    * `arrival_city`: the trip arrival city
    * `arrival_address`: the trip arrival adress
    * `arrival_point`: the arrival geographical point for the trip
    * `regular`: Is the trip a regular one ? True = Yes
    * `date`: the date of the trip (*required*)
    * `interval_min`: nomber of interval (days) accepted before the departure date
    * `interval_max`: nomber of interval (days) accepted after the departure date
    * `dows`: if the trip is a regular one, dows contains a Json array containing days of weeks. (*required if the trip is regular*)
    * `comment`: an optionnal comment for this trip
    * `demand`: True or False
    * `offer`: True or False
    * `demand_radius`: perimeter of the passenger search
    * `demand_smokers_accepted`: weather the passenger accepts smokers or not
    * `demand_pets_accepted`: weather the passenger accepts pets or not
    * `demand_place_for_luggage`:  weather the passenger need place for laggages or not
    * `demand_car_type`: the car type id asked by the passenger
    * `demand_min_remaining_seats`:  the number of remaining seats for the passenger
    * `demand_max_km_price`: Maximum price per KM
    * `offer_radius`: perimeter of the conductor search
    * `offer_checkpoints`: checkpoints of the offer trip
    * `offer_route`: SIG route
    * `offer_km_price`: Price per KM asked by the driver
    * `offer_radius`: perimeter of the passenger search
    * `offer_smokers_accepted`: weather the passenger accepts smokers or not
    * `offer_pets_accepted`: weather the passenger accepts pets or not
    * `offer_place_for_luggage`:  weather the driver have place for laggages or not
    * `offer_car_type`: the car type the driver have
    * `offer_seats_available`:  the number of remaining seats for the driver
    
Example::

    $ curl -X PUT http://api.bisonvert.net/trips/27/ -d 'alert=on&arrival_city=paris&arrival_point=POINT(2.3509871 48.85666670000002)&comment=&date=25/01/2010&demand-passenger_car_type=&demand-passenger_max_km_price=&demand-passenger_min_remaining_seats=&demand-passenger_pets_accepted=on&demand-passenger_smokers_accepted=on&demand-radius=500&departure_address=&departure_city=toulouse&departure_point=POINT(1.4429513 43.60436300000001)&interval_max=0&interval_min=7&name=announce name&offer-radius=500&offer-route=&offer-steps=&regular=False&return_trip=false&time=8&trip_type=1'
    OK

Delete
------

Delete an existing trip offer/demand object. 

**URL**
    /trips/id
*Verb*
    DELETE
*Data*
    None
    
Example::

    $ curl -X DELETE http://api.bisonvert.net/trips/27/
    OK
