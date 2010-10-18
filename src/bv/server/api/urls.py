# django imports
from django.conf.urls.defaults import *

# piston imports
from piston.authentication import OAuthAuthentication, HttpBasicAuthentication
from piston.doc import documentation_view

# API imports
from bv.server.api.resource import Resource
from bv.server.api.carpoolhandlers import TripsHandler, TripsSearchHandler 
from bv.server.api.ratinghandlers import RatingsHandler, TempRatingsHandler
from bv.server.api.ratinghandlers import MyRatingsHandler, RatingsAboutMeHandler
from bv.server.api.talkshandlers import TalksHandler, MessagesHandler
from bv.server.api.usershandlers import UsersHandler
from bv.server.api.citieshandlers import CitiesHandler
from bv.server.api.cartypeshandlers import CarTypesHandler

# auth
# auth = [OAuthAuthentication(), HttpBasicAuthentication()]
auth = HttpBasicAuthentication()
noauth = None

# trips
trips_handler = Resource(handler=TripsHandler, authentication=auth)
trip_search_handler = Resource(handler=TripsSearchHandler, authentication=auth)

# ratings
ratings_handler = Resource(handler=RatingsHandler, authentication=auth)
my_ratings_handler = Resource(handler=MyRatingsHandler, authentication=auth)
tempratings_handler = Resource(handler=TempRatingsHandler, authentication=auth)
ratings_about_me_handler = Resource(handler=RatingsAboutMeHandler, authentication=auth)

talks_handler = Resource(handler=TalksHandler, authentication=auth) # talks
messages_handler = Resource(handler=MessagesHandler, authentication=auth) # messages
users_handler = Resource(handler=UsersHandler, authentication=auth) # users
cities_handler = Resource(handler=CitiesHandler) # cities
cartypes_handler = Resource(handler=CarTypesHandler) # cartypes

# Carpool URLs
urlpatterns = patterns('bv.server.api.handlers',
    # trips
    url(r'^trips/search/(?P<trip_id>\d+)/$', trip_search_handler),
    url(r'^trips/search/$', trip_search_handler),   
    url(r'^trips/(?P<trip_id>[0-9a-z\_]+)/$', trips_handler),
    url(r'^trips/$', trips_handler),

    
    url(r'^temp-ratings/$', tempratings_handler),
    url(r'^temp-ratings/(?P<id>\d+)/$', tempratings_handler),
    
    # ratings
    url(r'^ratings/(?P<id>\d+)/$', ratings_handler),
    url(r'^ratings/$', ratings_handler),
    url(r'^ratings/received/$', ratings_about_me_handler),
    url(r'^ratings/given/$', my_ratings_handler),

    # talks
    url(r'^talks/$', talks_handler),
    url(r'^talks/(?P<talk_id>[0-9a-z\_]+)/$', talks_handler),
    url(r'^talks/(?P<talk_id>\d+)/messages/(?P<message_id>[0-9a-z\_]+)/$', messages_handler),
    url(r'^talks/(?P<talk_id>\d+)/messages/$', messages_handler),

    # users
    url(r'^users/(?P<user_id>.+)/$', users_handler),
    
    # cities
    url(r'^cities/(?P<query>.+)/$', cities_handler),

    # cartypes
    url(r'^cartypes/$', cartypes_handler),
)

urlpatterns += patterns('bv.server.api.gis_utils', 
    url(r'^gis/calculate_buffer/$', 'calculate_buffer', {}, 'calculate_buffer'),
    url(r'^gis/ogcserver/$', 'ogcserver', {}, 'ogcserver'),
)

