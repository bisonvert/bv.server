"""
Register
--------

To access the API, your access have to be granted by us; You'll have a consumer
key and a consumer secret. It's possible to register online, via our site (see
http://www.bisonvert.net/api/) and internally, here is the way::

    >>> from django.contrib.auth.models import User
    >>> user = User.objects.get(username="test")
    >>> from piston.models import Consumer
    >>> consumer = Consumer(name='test', user=user)
    >>> consumer.status = "accepted"
    >>> consumer.generate_random_codes()
    >>> consumer.key
    ...
    >>> consumer.secret
    ...
    
Obtain a Request Token
----------------------

Once your account registred, you may want to access your data, stored on the 
server. For this purpose, you need to have a request token::

    >>> from django.test.client import Client
    >>> c = Client()
    >>> response = c.get("/api/request_token/")
    >>> response.status_code
    401
    >>> # depends on REALM_KEY_NAME Django setting
    >>> response._headers['www-authenticate']
    ('WWW-Authenticate', 'OAuth realm=""')
    >>> response.content
    'Invalid request parameters.'

The Consumer sends the following HTTP POST request to the Service Provider::

    >>> import time
    >>> parameters = {
    ...     'oauth_consumer_key': consumer.key,
    ...     'oauth_signature_method': 'PLAINTEXT',
    ...     'oauth_signature': '%s&' % consumer.secret,
    ...     'oauth_timestamp': str(int(time.time())),
    ...     'oauth_nonce': 'requestnonce',
    ...     'oauth_version': '1.0',
    ...     'oauth_callback': 'http://localhost:200/request_token_ready',
    ... }
    
    >>> response = c.get("/api/request_token/", parameters)
    >>> parameters = {
    ...     'oauth_consumer_key': "woITVJD9OqNoGfkx2xpeuA",
    ...     'oauth_signature_method': 'PLAINTEXT',
    ...     'oauth_signature': '%s&' % "3K0k75GaNjjp8R1NsQMIhfXs0OJOWVxIKwhsLCfEcA",
    ...     'oauth_timestamp': str(int(time.time())),
    ...     'oauth_nonce': 'requestnonce',
    ...     'oauth_version': '1.0',
    ...     'oauth_callback': 'http://localhost:200/callback',
    ... }
    >>> import httplib2
    >>> import urllib
    >>> h = httplib2.Http()
    >>> h.request('http://twitter.com/oauth/request_token', 'GET', urllib.urlencode(parameters))

The Service Provider checks the signature and replies with an unauthorized 
Request Token in the body of the HTTP response::

    >>> response.status_code
    200
    >>> response.content
    'oauth_token_secret=...&oauth_token=...&oauth_callback_confirmed=true'
    >>> from piston.models import Token
    >>> token = list(Token.objects.all())[-1]
    >>> token.key in response.content, token.secret in response.content
    (True, True)
    >>> token.callback, token.callback_confirmed
    (u'http://printer.example.com/request_token_ready', True)

If you try to access a resource with a wrong scope, it will return an error::

    >>> parameters['scope'] = 'videos'
    >>> response = c.get("/oauth/request_token/", parameters)
    >>> response.status_code
    401
    >>> response.content
    'Resource videos does not exist.'
    >>> parameters['scope'] = 'photos' # restore

If you try to put a wrong callback, it will return an error::

    >>> parameters['oauth_callback'] = 'wrongcallback'
    >>> response = c.get("/oauth/request_token/", parameters)
    >>> response.status_code
    401
    >>> response.content
    'Invalid callback URL.'

Requesting User Authorization
-----------------------------

The Consumer redirects your browser to the Service Provider User 
Authorization URL to obtain the user approval for accessing it's protected 
resources.

The Service Provider asks Jane to sign-in using her username and password::

    >>> parameters = {
    ...     'oauth_token': token.key,
    ... }
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> response.status_code
    302
    >>> response['Location']
    'http://.../accounts/login/?next=/oauth/authorize/%3Foauth_token%3D...'
    >>> token.key in response['Location']
    True

If successful, asks her if she approves granting printer.example.com access to 
her private photos. If Jane approves the request, the Service Provider 
redirects her back to the Consumer's callback URL::

    >>> c.login(username='jane', password='toto')
    True
    >>> token.is_approved
    0
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> response.status_code
    200
    >>> response.content
    'Fake authorize view for printer.example.com.'
    
    >>> # fake authorization by the user
    >>> parameters['authorize_access'] = 1
    >>> response = c.post("/oauth/authorize/", parameters)
    >>> response.status_code
    302
    >>> response['Location']
    'http://printer.example.com/request_token_ready?oauth_verifier=...&oauth_token=...'
    >>> token = list(Token.objects.all())[-1]
    >>> token.key in response['Location']
    True
    >>> token.is_approved
    1

    >>> # without session parameter (previous POST removed it)
    >>> response = c.post("/oauth/authorize/", parameters)
    >>> response.status_code
    401
    >>> response.content
    'Action not allowed.'
    
    >>> # fake access not granted by the user (set session parameter again)
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> parameters['authorize_access'] = 0
    >>> response = c.post("/oauth/authorize/", parameters)
    >>> response.status_code
    302
    >>> response['Location']
    'http://printer.example.com/request_token_ready?error=Access%20not%20granted%20by%20user.'
    >>> c.logout()

With OAuth 1.0a, the callback argument can be set to "oob" (out-of-band), 
you can specify your own default callback view with the
``OAUTH_CALLBACK_VIEW`` setting::

    >>> from oauth_provider.consts import OUT_OF_BAND
    >>> token.callback = OUT_OF_BAND
    >>> token.save()
    >>> parameters = {
    ...     'oauth_token': token.key,
    ... }
    >>> c.login(username='jane', password='toto')
    True
    >>> response = c.get("/oauth/authorize/", parameters)
    >>> parameters['authorize_access'] = 0
    >>> response = c.post("/oauth/authorize/", parameters)
    >>> response.status_code
    200
    >>> response.content
    'Fake callback view.'
    >>> c.logout()

"""
