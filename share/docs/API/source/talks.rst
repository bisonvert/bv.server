Talks API
=========

You can send messages to other users when you have to. For this, we provide a
talks API.

There are `talks` and `messages`. A `talk` contains `messages`, and a `message`
is linked to a `talk`

Talks
~~~~~

Talks are also aften called "negociations". Their goal are to initiate a 
discussion between two users: the authenticated one, and another one, specified
by the first one.

A talk is always related to a Trip.

List
----

**URL**
    /api/talks/
*Verb*
    GET
*Data*
    None

List all existing talks for the authenticated user::

    $ curl -X GET http://localhost:8000/api/talks/
    [
        {
            "id": 18, 
            "from_user": {
                "username": "test", 
                "id": 5
            }, 
            "trip": {
                "date": "2020-01-20", 
                "time": null, 
                "departure_city": "Lavaur (81)", 
                "id": 27, 
                "arrival_city": "Paris"
            }, 
            "creation_date": "2010-02-01 14:10:21"
        }, 
        {
            "id": 19, 
            "from_user": {
                "username": "test", 
                "id": 5
            }, 
            "trip": {
                "date": "2020-01-20", 
                "time": "09:00:00", 
                "departure_city": "toulouse", 
                "id": 28, 
                "arrival_city": "paris"
            }, 
            "creation_date": "2010-02-01 14:11:42"
        }
    ]

Validate
--------

**URL**
    /api/talks/id    
*Verb*
    PUT
*Data*
    `validate`: must be set to 'True' to have effect.
    
Validate the negociation talk. This deletes the talk, and create a temporary 
report ::
    
    $ curl -X PUT http://localhost:8000/api/talks/18/ -d "validate=true"
    OK
    
Delete
------

We don't really delete a talk, but we cancel it, with an explanation message.
For this purpose, we make a PUT instead of a DELETE.

**URL**
    /api/talks/id    
*Verb*
    PUT
*Data*
    * `cancel`: must be set to 'True' to have effect.
    
Cancel the negotiation talk
    
Delete the negociation talk and associated messages and send a mail to the other
user. 

Deleting a talk is only possible for one of the two users the talk is about::

    $ curl -X PUT http://localhost:8000/api/talks/19/ -d "cancel=true&message='my+message'"

Create
------

Initiate the talk with another user::
    
    $ curl -X POST http://localhost:8000/api/talks/ -d "trip_id=28&message='my+message'"
    Created

Messages
~~~~~~~~

Messages are always related to a talk. They represents an exchange between 
users.

List
----

**URL**
    /api/talks/messages/:talk_id/
*Verb*
    GET
*Data*
    None

Return the list of messages in a talk. The authenticated user must be one of 
the two of the talk::

    $ curl -X GET http://localhost:8000/api/talks/22/messages/
    [
        {
            "date": "2010-02-01 15:13:47", 
            "message": "'my message'", 
            "id": 28, 
            "talk": {
                "id": 22, 
                "from_user": {
                    "username": "test", 
                    "id": 5
                }, 
                "trip": {
                    "date": "2020-01-20", 
                    "time": "09:00:00", 
                    "departure_city": "toulouse", 
                    "id": 28, 
                    "arrival_city": "paris"
                }, 
                "creation_date": "2010-02-01 15:13:47"
            }, 
            "from_user": true
        }, 
        {
            "date": "2010-02-01 15:33:45", 
            "message": "'my message (2nd)'", 
            "id": 29, 
            "talk": {
                "id": 22, 
                "from_user": {
                    "username": "test", 
                    "id": 5
                }, 
                "trip": {
                    "date": "2020-01-20", 
                    "time": "09:00:00", 
                    "departure_city": "toulouse", 
                    "id": 28, 
                    "arrival_city": "paris"
                }, 
                "creation_date": "2010-02-01 15:13:47"
            }, 
            "from_user": true
        }
    ]

New
---

**URL**
    /api/talks/messages/
*Verb*
    PUT
*Data*
    * `trip_id`: the related trip the user want to talk about

Send a message to the author of the trip announce. If the Talk does not exists, 
create it automatically::

    $ curl -X POST http://localhost:8000/api/talks/22/messages/ -d "message='my+message+(2nd)'"
    OK

Delete
------

It's not possible to delete a single message. You can delete an entire talk, 
and, by the way, all related messages.
