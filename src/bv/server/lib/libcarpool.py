# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
"""Provides a common way to interact with bisonvert serverside carpool data 
(search, list, add, edit and delete trips)

"""
#python import
import datetime 

#django imports
from django.conf import settings
from django.contrib.gis.geos import MultiPoint, GEOSGeometry
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode
from django.utils import simplejson

#ecov imports
from bv.server.carpool import get_direction_route, str_slugify
from bv.server.carpool.models import City, Trip, TripDemand, TripOffer
from bv.server.carpool.misc import sort_offers, sort_demands
from bv.server.carpool.forms import EditTripOfferOptionsForm, EditTripDemandOptionsForm, \
    EditTripForm

from bv.server.carpool.forms import DynamicEditTripForm, DynamicEditTripOfferOptionsForm, DynamicEditTripDemandOptionsForm

# lib import
from bv.server.utils.paginator import PaginatorRender
from bv.server.lib.exceptions import *


__fixtures__ = ['accounts.json','lib_cities.json','lib_trips.json',]

class LibCarpool:
    
    TRIPOFFER = Trip.OFFER
    TRIPDEMAND = Trip.DEMAND
    MAX_TRIPS = 30
    OFFER_RADIUS = 500
    DEMAND_RADIUS = 500
    INTERVAL_MIN = 0
    INTERVAL_MAX = 0
    
    def _get_ordering(self):
        return {
            'departure': ['departure_city'],
            '-departure': ['-departure_city'],
            'arrival': ['arrival_city'],
            '-arrival': ['-arrival_city'],
            'date': ['dows', 'date'],
            '-date': ['-dows', '-date'],
            'time': ['time'],
            '-time': ['-time'],
            'type': ['type'],
            '-type': ['-type'],
            'alert': ['-alert'],
            '-alert': ['alert'],                
        }
    
    def get_trip_details(self, departure_slug, departure_zip, arrival_slug, arrival_zip):
        """Return details about departure and arrival given emplacements. Fetch 
        information from cities data, compute GIS points and return them in 
        a dict.
        
        """
        departure_city = self.get_city(departure_slug, departure_zip)
        arrival_city = self.get_city(arrival_slug, arrival_zip)
        
        return {
            'departure': {
                'name': smart_unicode(departure_city), 
                'point': departure_city.point.wkt, 
                'favoriteplace': None
            },
            'arrival': {
                'name': smart_unicode(arrival_city), 
                'point': arrival_city.point.wkt, 
                'favoriteplace': None
            },
        }    
        
    ## REFACTOR : not used
    def get_trip_geometry_from_details(self, trip_details=None, departure_slug=None, 
            departure_zip=None, arrival_slug=None, arrival_zip=None):
        """Compute and return a GIS multipoint geometry, based on trip_type and 
        additional data provided in parameters.
        
        If trip_details is not known when doing the call, you can pass departure
        and arrival slug and zipcode, the lib can find them the right way.

        """
        if (not trip_details and departure_slug 
                and departure_zip and arrival_slug and arrival_zip):
            trip_details = self.get_trip_details(departure_slug, departure_zip, 
                    arrival_slug, arrival_zip)
        try:
            mpoints = MultiPoint([GEOSGeometry(trip_details['departure']['point']), 
                GEOSGeometry(trip_details['arrival']['point'])])
        except:
            raise ErrorException()

        return mpoints.envelope.wkt
        
    def get_city(self, slug, zipcode):
        """Return a city object from slug and zipcode informations
        
        Raises a CityNotfound exception if the city doenst exists        
        """
        slug = unicode(slug)
        try:
            zipcode = int(zipcode)
            return City.objects.get(slug=str_slugify(slug), zipcode__gte=zipcode*1000, zipcode__lte=(zipcode+1)*1000)
        except City.DoesNotExist:
            raise CityDoesNotExist()
    
    def list_trips_by_type(self, offer_details, demand_details, user, trip_type, maximum):
        """Return a list of trips, for the trip_type given in parameter
        
        If trip_type is not contained in TRIPOFFER or TRIPDEMAND, raise a 
        InvalidTripType exception
        
        """
        if trip_type == self.TRIPOFFER:
            # search for offers
            (radius, date, interval_min, interval_max, departure_point,
                arrival_point) = offer_details
                
        elif trip_type == self.TRIPDEMAND:
            #search for demands
            (radius, date, interval_min, interval_max, route, departure_point,
                arrival_point) = demand_details
            if route is None or route.geom_type != 'LineString':
                raise InvalidGeometry("the demand geometry type must be a LineString")
        else:
            raise InvalidTripType()
            
        if trip_type == self.TRIPOFFER:
            trips = Trip.objects.get_offers(departure_point, arrival_point, radius)
        else:
            trips = Trip.objects.get_demands(route, get_direction_route(route), radius)
        trips = trips.get_mark_details()

        # adding common date clause
        trips = trips.filter_date_interval(date, interval_min, interval_max).exclude_outdated()
        # exclude my trips ?
        if settings.EXCLUDE_MY_TRIPS and user.is_authenticated():
            trips = trips.exclude(user=user)
        # ordering and limit
        trips = trips.order_by('-pourcentage_rank')[:maximum]

        if trip_search_type == self.TRIPOFFER:
            trips = sort_offers(trips, date, interval_min, interval_max)
        else:
            trips = sort_demands(trips, date, interval_min, interval_max)
        
        return trips
    
    def list_trips(self, ordered_by='date'):
        """Return a list of trips, ordered by the "ordered_by" parameter
        
        """
        ordering = self._get_ordering()
        order_args = ordering[ordered_by]
        return Trip.objects.exclude_outdated().extra(select={'type': 'CASE WHEN demand_id IS NULL THEN 0 WHEN offer_id IS NULL THEN 1 ELSE 2 END'}).order_by(*order_args)
        
    def get_trip_list_paginator(self, page, pagination, available_paginations, 
            ordered_by, url_pagination, url):
        """Return a paginator for the list of trips.
        
        Uses the list_trips method
        
        """
        trips = list_trips_by_user(ordered_by)
        return PaginatorRender(
            trips,
            page,
            pagination,
            allow_empty_first_page=True,
            extra_context = {
                'paginations': available_paginations,
                'get_url_pg': url_pagination,
                'get_url': url,
                'order': ordered_by,
            }
        )
    
    def list_trips_with_departure_or_arrival(self, city, is_departure, ordered_by='date', radius=10000):
        """Return a list of trips witch matches the given city as a departure or
        an arrival point (specified with the "is_departure" parameter), using the
        radius given in parameter.
        
        Exemple: Get all trips with a departure or arrival city at "toulouse".

        """
        ordering = self._get_ordering()
        oargs = ordering[ordered_by]

        if is_departure:
            trips = Trip.objects.get_trip_from_city(city.point, radius).exclude_outdated().order_by(*oargs)
        else:
            trips = Trip.objects.get_trip_to_city(city.point, radius).exclude_outdated().order_by(*oargs)
        
        return trips
    
    def get_trip_list_paginator_with_departure_or_arrival(self, city, is_departure, 
            ordered_by, page, pagination, available_paginations, 
            url_pagination=None, url_pagination_order=None):
        """Return a paginator for the list of trips matching given city as an 
        arrival or a departure point.

        """
        if (not pagination):
            url_pagination = self._get_pagination_url(pagination)
        if (not url_pagination_order):
            url_pagination_order = self._get_pagination_url_with_order(pagination, ordered_by)
        
        trips = self.list_trips_with_departure_or_arrival(city, is_departure, ordered_by)
        return PaginatorRender(
            trips,
            page,
            pagination,
            allow_empty_first_page=True,
            extra_context = {
                'city': city,
                'is_depart': is_departure,
                'paginations': available_paginations,
                'get_url_pg': url_pagination,
                'get_url': url_pagination_order,
                'order': ordered_by,
            }
        )
    
    def _get_pagination_url(self, pagination):
        """Return the url used by paginator for paginating record displaying.
        
        """
        return '?pg=%d' % pagination
        
    def _get_pagination_url_with_order(self, pagination, order):
        """Return the url used by paginator for paginating record displaying, 
        when using an order clause.
        
        """    
        return '?pg=%d&order=%s' % (pagination, order)
        
    def list_trips_by_user(self, user, ordered_by='date'):
        """Returns a list of trips for a given user
        
        """
        ordering = self._get_ordering()
        oargs = ordering[ordered_by]
        return user.trip_set.all().extra(select={'type': 'CASE WHEN demand_id IS NULL THEN 0 WHEN offer_id IS NULL THEN 1 ELSE 2 END'}).order_by(*oargs)
        
    def get_list_by_user_paginator(self, user, page, pagination, 
            available_paginations, ordered_by, url_pagination, url):
        """Return a paginator of the list of trips for a given user

        """
        
        trips = self.get_user_trips(user, ordered_by)
        return PaginatorRender(
            trips,
            page,
            pagination,
            allow_empty_first_page=True,
            extra_context = {
                'current_item': 10,
                'paginations': available_paginations,
                'get_url_pg': url_pagination,
                'get_url': url,
                'order': ordered_by,
            }
        )


    def _format_dict2model(self, data, *prefixes):
        """Replace '_' by '-' in the fields keys, so that it can be understand
        as valid input data by forms that have prefix.

        Exception will be thrown if this modification leads to keys with same name.
        """
        dct = {}
        for k, v in data.iteritems():
            for p in prefixes:
                if k.startswith(p + '_'):
                    print "%s will be reformated" % k
                    k = k[:len(p)] + '-'  + k[len(p)+1:]
                    break
            if k not in dct:
                dct[k] = v
            else:
                raise Exception("Args have the same name after being reformated _ to - : %s" % k)

        return dct


    def _add_or_edit_trip(self, user, post_data, trip_id=None,
            formfactory={'trip'      : EditTripForm,
                         'tripoffer' : EditTripOfferOptionsForm,
                         'tripdemand': EditTripDemandOptionsForm}):
        """Add or edit a trip.
        
        If a trip id is specified, retreive it and edit it (save it if needed)
        If no trip id is specified, create a new new trip and process it.

        :post_data: can be in the form - or _ for offer and demand forms.
                    but it needs to be prefixed by offer or demand.
        """

        # XXX do not touch to these prefix, they are used in many places as hard values
        offer_prefix = "offer"
        demand_prefix = "demand"
        models_data = self._format_dict2model(post_data, offer_prefix, demand_prefix)

        trip_form = formfactory['trip']
        tripoffer_form = formfactory['tripoffer']
        tripdemand_form = formfactory['tripdemand']
        
        if trip_id:
            trip = Trip.objects.get(id=trip_id, user=user)
            form_offer = tripoffer_form(data=models_data, instance=trip.offer, prefix=offer_prefix)
            form_demand = tripdemand_form(data=models_data, instance=trip.demand, prefix=demand_prefix)
        else:
            trip = Trip(user=user)
            form_offer = tripoffer_form(data=models_data, prefix=offer_prefix)
            form_demand = tripdemand_form(data=models_data, prefix=demand_prefix)

        form_trip = trip_form(data=models_data, instance=trip)

        
        error = False
        if form_trip.is_valid():
            trip_type = int(form_trip['trip_type'].data)
            trip = form_trip.save(commit=False)
            
            if trip_type != self.TRIPDEMAND : 
                if form_offer.is_valid():
                    offer = form_offer.save(commit=False)
                    offer.steps = simplejson.loads(form_offer.cleaned_data['steps'])
                    offer.save()
                    trip.offer = offer
                else:
                    error = form_offer.errors()
                
            if trip_type != self.TRIPOFFER:
                if form_demand.is_valid():
                    trip.demand = form_demand.save()
                else:
                    error = True
            if not error:
                # if we have an offer, and a demand is already registred, delete it 
                if trip_type == self.TRIPOFFER and trip.demand is not None: 
                    trip.demand.delete()
                    trip.demand = None 
                
                # if we have a demand, and an offer is already registred, delete it   
                if trip_type == self.TRIPDEMAND and trip.offer is not None: 
                    trip.offer.delete()
                    trip.offer = None

                trip.save()
        else:
            error = True
        return {
            'form_demand': form_demand,
            'form_offer': form_offer,
            'form_trip': form_trip,
            'trip': trip,
            'error': error,
        }

        
    def create_trip(self, user, post_data):
        """Create a new trip
        
        "post_data" must be a python dict with valid data.
        
        """
        return self._add_or_edit_trip(user, post_data)
    
    def update_trip(self, user, post_data, trip_id):
        """Update an existing trip
        
        """
        return self._add_or_edit_trip(user, post_data, trip_id)

    def reduced_update_trip(self, user, post_data, trip_id):
        """Only updates small part of the trip: radius and interval min/max"""

        ff = {'trip'       : DynamicEditTripForm, 
              'tripoffer'  : DynamicEditTripOfferOptionsForm,
              'tripdemand' : DynamicEditTripDemandOptionsForm, 
             }
        return self._add_or_edit_trip(user, post_data, trip_id, formfactory=ff)
    
    def get_trip_results(self, is_offer=None, is_demand=None, offer_radius=None, 
            demand_radius=None, date=None, interval_min=None, interval_max=None, 
            is_regular=None, dows=None, offer_route=None, departure_point=None, 
            arrival_point=None, max_trips=None, trip_id=None, user=None):
        """Return a list containing the trip object, trip_offers and 
        trip_demands matching given criterias.
        
        """
        # vars initialisation
        max_trips = max_trips or self.MAX_TRIPS
        trip = None
        trip_offers = None
        trip_demands = None
        
        if trip_id and user:
            # return matching trips with an already existing search
            try:
                trip = Trip.objects.get(pk=int(trip_id), user=user)
            except Trip.DoesNotExist:
                raise InvalidUser(user)
                
            if is_offer or trip.offer:
                is_offer = is_offer or True
                offer_radius = offer_radius or trip.offer.radius
                offer_route = offer_route or trip.offer.route
                    
            if (is_demand or trip.demand):
                is_demand = is_demand or True
                demand_radius = demand_radius or trip.demand.radius
            is_regular = is_regular or trip.regular
            date = date or trip.date
            dows = dows or trip.dows
            interval_min = interval_min or trip.interval_min
            interval_max = interval_max or trip.interval_max
            departure_point = departure_point or trip.departure_point
            arrival_point = arrival_point or trip.arrival_point
            
        if is_offer:
            offer_radius = offer_radius or self.OFFER_RADIUS
            if trip_id:
                if offer_route is None or offer_route.geom_type != 'MultiLineString':
                    raise InvalidGeometry("The trip offer route geometry is " \
                    "required and need to be a 'MultiLineString'. You gave us " \
                    "a '%(type)s' instead." % {
                        'type': "None" if offer_route is None else offer_route.geom_type
                    })
            else:
                if offer_route is None or offer_route.geom_type != 'LineString':
                    raise InvalidGeometry("The trip offer route geometry is " \
                    "required and need to be a 'LineString'. You gave us " \
                    "a '%(type)s' instead." % {
                        'type': "None" if offer_route is None else offer_route.geom_type
                    })
                    
        if is_demand:
            demand_radius = demand_radius or self.DEMAND_RADIUS
       
        interval_min = interval_min or self.INTERVAL_MIN
        interval_max = interval_max or self.INTERVAL_MAX
        today = datetime.date.today()
        date = date or today            
        
        if is_demand:
            trip_offers = Trip.objects.get_offers(departure_point, arrival_point, demand_radius)
            if trip_id:
                trip_offers = trip_offers.exclude(pk=trip_id)
            trip_offers = trip_offers.get_mark_details()
            
            if is_regular:
                trip_offers = trip_offers.filter_dows(dows)
            else:
                trip_offers = trip_offers.filter_date_interval(date, interval_min, interval_max)
            trip_offers = trip_offers.exclude_outdated(today)
            # exclude my trips ?
            if settings.EXCLUDE_MY_TRIPS:
                trip_offers = trip_offers.exclude(user=user)
            # ordering and limit
            trip_offers = trip_offers.order_by('-pourcentage_rank')[:max_trips]
            trip_offers = sort_offers(trip_offers, date, interval_min, interval_max, trip=trip)

        if is_offer:
            trip_demands = Trip.objects.get_demands(offer_route, get_direction_route(offer_route), offer_radius)
            if trip_id:
                trip_demands = trip_demands.exclude(pk=trip_id)
            trip_demands = trip_demands.get_mark_details()
            if is_regular:
                trip_demands = trip_demands.filter_dows(dows)
            else:
                trip_demands = trip_demands.filter_date_interval(date, interval_min, interval_max)
            trip_demands = trip_demands.exclude_outdated(today)
            # exclude my trips ?
            if settings.EXCLUDE_MY_TRIPS:
                trip_demands = trip_demands.exclude(user=user)
            # ordering and limit
            trip_demands = trip_demands.order_by('-pourcentage_rank')[:max_trips]
            trip_demands = sort_demands(trip_demands, date, interval_min, interval_max, trip=trip)

        return{
            'trip': trip,
            'trip_demands': trip_demands,
            'trip_offers': trip_offers,
        }
        
    def delete_trip(self, trip_id, user):
        """Delete a trip.
        
        If the user is not the owner of the trip, raise an InvalidUser exception

        """
        try:
            trip = Trip.objects.get(pk=trip_id, user=user)
            trip.delete()
        except Trip.DoesNotExist as e:
            if not Trip.objects.get(pk=trip_id):
                raise e
            else:
                raise InvalidUser('given user have no rights to delete this trip')
    
    def switch_trip_alert(self, user, trip_id, value=None):
        """Switch the alert (on/off) for a specified trip.

        If no value is specified, just switch the value on or off, regarding 
        the current state.
        """
        trip = get_object_or_404(Trip, pk=trip_id, user=user)
        if value == None:
            value = not trip.alert
        trip.alert = value
        trip.save()
        
    def get_trip(self, trip_id):
        """Return a trip by it's id.
        
        """
        return get_object_or_404(Trip.objects.get_mark_details(), pk=trip_id) 

