from bv.server.api.handlers import Handler, AnonymousHandler, paginate_items
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

from bv.server.carpool.models import Trip, TripDemand, TripOffer
from bv.server.lib import LibCarpool
from bv.server.lib.exceptions import InvalidUser

from bv.server.carpool.forms import EditTripForm, EditTripOfferOptionsForm, \
    EditTripDemandOptionsForm

from django.contrib.gis.geos.geometry import GEOSGeometry
from datetime import date
from piston.decorator import decorator

from django.conf import settings

__trip_public_fields__ = (
'id', 
'departure_point',
'departure_city',
'departure_address', 
'arrival_point', 
'arrival_city', 
'arrival_address',
'date', 
'interval_min', 
'interval_max',
'regular', 
'dows', 
'time',
'creation_date', 
'modification_date', 
('offer', (
    'id',
    'driver_km_price',
    'driver_pets_accepted',
    'direction_route',
    'driver_car_type_id',
    'driver_seats_available',
    'radius',
    'steps',
    'driver_smokers_accepted',
    'driver_place_for_luggage',
    'simple_route',
)),
'demand',
('user', (
    'id',
    'username',
)),
)

__trip_private_fields__ = __trip_public_fields__ + (
'name',
'alert', 
'comment',
)
__valid_search_keys__ = (
    'trip_id',
    'is_offer',
    'is_demand',
    'offer_radius',
    'demand_radius',
    'date', 
    'interval_min', 
    'interval_max', 
    'is_regular', 
    'dows', 
    'route', 
    'departure_point', 
    'arrival_point',
    'geometry',
)

def request_to_dict(request):
    """Transform a request into a dict, and split the dows field into a list.

    """
    requestdict = dict(request.REQUEST.items())
    if 'dows' in requestdict:
        requestdict['dows'] = request.REQUEST['dows'].split('-')
    return requestdict

class CarpoolHandler(Handler):
    count = settings.DEFAULT_PAGINATION_COUNT
    model = Trip
    fields = __trip_private_fields__
    def __init__(self):
        self.lib = LibCarpool()

class AnonymousCarpoolHandler(AnonymousHandler):
    count = settings.DEFAULT_PAGINATION_COUNT
    model = Trip
    fields = __trip_public_fields__
    def __init__(self):
        self.lib = LibCarpool()

def filter_tripsearch_values(dct):
    """Filter request values.
    
    """
    values = dict()
    for key, value in dct.iteritems():
        if key.encode() in __valid_search_keys__:
            if key in (u'departure_point', u'arrival_point', u'offer_route', u'geometry'):
                value = GEOSGeometry(value)
            if key == u'date':
                value = date(*[int(datevalue) for datevalue in value.encode().split('-')])
            if key == u'geometry':
                values['offer_route'] = value
            else:
                if key =='interval_min' or key == 'interval_max':
                    value = int(value)
                values[key.encode()] = value
    return values

class AnonymousTripsSearchHandler(AnonymousCarpoolHandler):
    def read(self, request, **kwargs):
        """Make a search within the list of existing trips

        """
        return self.lib.get_trip_results(**kwargs)

class TripsSearchHandler(CarpoolHandler):
    anonymous = AnonymousTripsSearchHandler
    def read(self, request, **kwargs):
        """Private search"""

        values = filter_tripsearch_values(request_to_dict(request))
        if 'trip_id' in kwargs:
            return self.lib.get_trip_results(user=request.user, **values)
        else:
            return self.anonymous.read(AnonymousTripsSearchHandler(), request, **values)
            

class AnonymousTripsHandler(AnonymousCarpoolHandler):
    """Anonymous trip handler (allow reading)
    
    """
    def read(self, request, trip_id=None, start=None, count=None):
        if trip_id == 'count':
            return self.lib.list_trips().count()
        elif trip_id:
            return self.lib.get_trip(trip_id)
        else:
            items = self.lib.list_trips()
        return paginate_items(items, start, count, request, self.count)


class TripsHandler(CarpoolHandler):
    """Handler for trips: CRUD for authenticated users.
    
    """
    anonymous = AnonymousTripsHandler
    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')
    
    def read(self, request, trip_id=None, start=None, count=None):
        if trip_id == 'count_mine':
            return self.lib.list_trips_by_user(request.user).count()
        if trip_id == 'mine':
            items = self.lib.list_trips_by_user(request.user)
            return paginate_items(items, start, count, request, self.count)
        return self.anonymous.read(AnonymousTripsHandler(), request, trip_id, start, count)

    def create(self, request):
        """Create a new trip, with the given data information, and the 
        authenticated user.
        
        Return a rc.CREATED if the trip has been created
        
        """
        response = self.lib.create_trip(request.user, request_to_dict(request))
        if (response['error']):
            return rc.BAD_REQUEST
        elif (response['trip']):
            return response['trip']
    
    def update(self, request, *args, **kwargs):
        """Update an existing trip
        
        """
        trip_id = kwargs.get('trip_id', None)
        if len(request.REQUEST.items()) == 1 and request.REQUEST.has_key('alert'):
            self.lib.switch_trip_alert(request.user, trip_id, request.REQUEST['alert'].encode().lower() == 'true')
            return rc.ALL_OK
        
        response = self.lib.update_trip(request.user, request_to_dict(request), trip_id)
        if response['error']:
            return rc.BAD_REQUEST
        elif response['trip']:
            return response['trip']
        
    def delete(self, request, trip_id):
        """Delete an existing trip, if the authenticated user is the one who has
        created the trip.
        
        """
        try:
            self.lib.delete_trip(trip_id, request.user)
            return rc.DELETED
        except InvalidUser:
            return rc.FORBIDDEN
        except Trip.DoesNotExist:
            return rc.NOT_HERE
