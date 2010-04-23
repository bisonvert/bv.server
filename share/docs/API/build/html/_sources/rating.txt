Reports / Ratings API
=====================

Bison Vert comes with a system to make reports about the trips, once they had
been made.

List given ratings
-------------------

List ratings made *by* the authenticated user.

**URL**
    /api/ratings/given/
*Verb*
    GET
*Data*
    None
    
Example::
    
    $ curl -X GET http://localhost:8000/api/ratings/given/
    [
        {
            "comment": "Merci beaucoup, c'était très sympa :)", 
            "mark": 5, 
            "user": {
                "username": "alexis", 
                "id": 1
            }, 
            "from_user": {
                "username": "test", 
                "id": 5
            }, 
            "creation_date": "2010-01-26", 
            "id": 1
        }, 
        {
            "comment": "my comment", 
            "mark": 5, 
            "user": {
                "username": "alexis", 
                "id": 1
            }, 
            "from_user": {
                "username": "test", 
                "id": 5
            }, 
            "creation_date": "2010-01-26", 
            "id": 3
        }
    ]


List received ratings 
---------------------

List ratings made *about* the authenticated user (received by)

**URL**
    /api/ratings/received/
*Verb*
    GET
*Data*
    None

Exemple::

    $ curl -X GET http://localhost:8000/api/ratings/received/
    [
        {
            "comment": "merci :)", 
            "mark": 5, 
            "user": {
                "username": "test", 
                "id": 5
            }, 
            "from_user": {
                "username": "alexis", 
                "id": 1
            }, 
            "creation_date": "2010-01-26", 
            "id": 2
        }, 
        {
            "comment": "my comment", 
            "mark": 5, 
            "user": {
                "username": "test", 
                "id": 5
            }, 
            "from_user": {
                "username": "alexis", 
                "id": 1
            }, 
            "creation_date": "2010-01-26", 
            "id": 4
        }
    ]

List temporary ratings
----------------------

.. _ratings-temp_ratings:

List temporary ratings for the authenticated user. This list ratings user have
to make.

**URL**
    /api/temp-ratings/
*Verb*
    GET
*Data*
    None

Exemple::

    $ curl -X GET http://localhost:8000/api/temp-ratings/
    [
        {
            "user2": {
                "username": "test", 
                "id": 5
            }, 
            "end_date": "2020-02-05", 
            "user1": {
                "username": "test", 
                "id": 5
            }, 
            "report2_creation_date": null, 
            "dows": [], 
            "id": 1, 
            "report1_creation_date": null, 
            "departure_city": "toulouse", 
            "date": "2020-01-20", 
            "creation_date": "2010-01-25", 
            "type": 1, 
            "start_date": "2020-01-21", 
            "arrival_city": "paris"
        }
    ]

Get
---

Retreive a rating, by it's id. Need to concern the authenticated user to be
accessed.

**URL**
    /api/ratings/:id/
*Verb*
    GET
*Data*
    None
    
Example::
    
    $ curl -X GET http://localhost:8000/api/ratings/1/
    
    
Add
---

Rate an user about a trip. Note that a temporary rating must exists to rate an 
user about  a trip. See the "validation" clause of the :ref:`talks` API.

**URL**
    /api/ratings/:id/
*Verb*
    PUT
*Data*
    * `mark`: an int, between 0 and 5
    * `comment`: comment about the trip
    
Example::

    $ curl -X POST http://localhost:8000/api/ratings/1/ -d "mark=5&comment=my+comment"
    OK
    
