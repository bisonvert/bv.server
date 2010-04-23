OAuth implementation
====================

To authenticate users from Bison Vert, we use OAuth. 

Consume the API
----------------

Before you can access informations throught our API, you need to declare 
to us your application: http://www.bisonvert.net/api/access/create/

We will provide you the consumer key and secret you need to use our API.

OAuth URLS
----------

Request Token:
    http://bisonvert.net/oauth/request_token/
    
Access Token:
    http://bisonvert.net/oauth/access_token/

Authorize:
    http://bisonvert.net/oauth/authorize/

Please refer to the OAuth documentation to get more informations on how to use 
this.

Exemple
--------

Bison Vert comes with a fully fonctional client, that implement the tree legged
authentication flow. This client is coded in django and the source code is 
available on bitbucket.
