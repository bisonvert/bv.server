Authentication to the Bisonvert API.
#####################################

Even if you can do some basic operations on the bison vert resources, you'll
quickly need to authenticate on a server to have access to features like "saved
search", or to contact users.

You can authenticate your users using two sort of mechanisms: OAuth or BasicHttp
authentication. We *strongly* recommend to use OAuth, and some bisonvert servers
can turn off the basic authentication, because this let pass the users
credentials over the network, in a basic way.

You can find more information about OAuth on http://oauth.net/.

Authenticate through OAuth
==========================

To use OAuth, you need to register your application with your account, on the
bisonvert server. The default server we provide is accessible at 
http://api.bisonvert.net/.

Here are the steps you have to follow in order to use OAuth authentication.

Declare you application.
------------------------

Before you can access informations throught our API, you need to declare 
to us your application: http://api.bisonvert.net/api/access/create/

We will provide you the **consumer key** and **secret** you need to use our API.

OAuth URLS
----------

Request Token:
    http://api.bisonvert.net/oauth/request_token/
    
Access Token:
    http://api.bisonvert.net/oauth/access_token/

Authorize:
    http://api.bisonvert.net/oauth/authorize/

Please refer to the OAuth documentation to get more informations on how to use 
this.

Django applications
-------------------

If you need to connect a django application to an API through OAuth, you can
have a look to the reusable application we made when creating the default
bisonvert django client application: http://bitbucket.org/bisonvert/django-oauthclient/

Feel free to contribute or to open tickets if you need.

Basic HTTP authentication
==========================

As said before, you also can (but this is inadvisable) authenticate through a
simple basic HTTP authentication. You just have to specify your login and
password in the HTTP headers.

Using curl, this work like this::

    $ curl -X GET http://api.bisonvert.net/trips/ --user username:password

Once again, be careful ! Your user credentials will pass uncrypted over the
network.

Exemple on how to consume the API
==================================

You can find the source code of a simple client for bisonvert, wrote in python,
using the django framework. The code is available here:
http://bitbucket.org/bisonvert/bvclient/.

