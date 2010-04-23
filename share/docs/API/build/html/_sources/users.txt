User API
================

It's possible to access information about users thanks to the User API

Add
---

Add a new user to the Bison Vert application. 

**URL**
    /api/users/
*Verb*
    PUT
*Data*
    * `email` : the mail of the user (**required**)
    * `username`: the username used to login (**required**)
    * `password`: the associated password (**required**)
    * `firstname`
    * `lastname`
    * `phone`
    * `mobile_phone`
    * `home_address`
    * `home_zipcode`
    * `home_city`
    * `language`: FR or EN for now.
    
Retreive
--------

Retreive all informations about a specified user. It's only possible to ask 
informations about the authenticated user.

**URL**
    /api/users/active
*Verb*
    GET
*Data*
    None

Edit
----

Edit information about the current authenticated user.

**URL**
    /api/users/active
*Verb*
    POST
*Data*
    * `email` : the mail of the user
    * `username`: the username used to login
    * `password`: the associated password
    * `firstname`
    * `lastname`
    * `phone`
    * `mobile_phone`
    * `home_address`
    * `home_zipcode`
    * `home_city`
    * `language`: FR or EN for now.

Delete
------

**URL**
    /api/users/id
*Verb*
    DELETE
*Data*
    None
    
Delete the authenticated user
