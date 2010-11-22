# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

""" Utilities for trip views """

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, LineString, MultiLineString
from django.http import HttpResponse, Http404
from django.utils import simplejson
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.utils import simplejson

from bv.server.carpool import MAX_DISTANCE_DRIVER, MAX_DISTANCE_PASSENGER, MAX_INTERVAL, SRID_DEFAULT, SRID_TRANSFORM, str_slugify
#from bv.server.carpool.models import City
from bv.server.utils.fields import FRENCH_DATE_INPUT_FORMATS
from bv.server.utils.geodjango import smart_transform
from bv.server.carpool.models import City

import datetime
import time

def get_mark_average(sum, num):
    if num == 0:
        return ""
    average = round(round(sum * 2.0 / num) / 2.0, 1)
    return get_mark_imgs(average, 'l')

def get_mark_imgs(mark, format=''):
    lim = int(mark)
    imgs = ['<img src="%simg/rating/%smark1.png" alt="%s/5" />' % (settings.MEDIA_URL, format, mark) for _ in range(0, lim)]
    if mark - lim == 0.5:
        imgs += ['<img src="%simg/rating/%smark0.5.png" alt="%s/5" />' % (settings.MEDIA_URL, format, mark)]
        lim += 1
    imgs += ['<img src="%simg/rating/%smark0.png" alt="%s/5" />' % (settings.MEDIA_URL, format, mark) for _ in range(lim, 5)]
    return mark_safe(''.join(imgs))

def calculate_buffer(request):
    """ Calculate a buffer around a geometry """
    poly_buffer = get_geometry_buffer(request.REQUEST)
    if poly_buffer is None:
        raise Http404

    response_dict = {
        'buffer': poly_buffer.wkt
    }

    resp = HttpResponse()
    simplejson.dump(response_dict , resp, ensure_ascii=False, separators=(',',':'))
    return resp

def get_geometry_buffer(parameters):
    """ Get the geometry passed into parameters (GET or POST) """
    radius = 0
    poly_buffer = None
    try:
        if parameters.has_key('radius'):
            radius = min(abs(int(parameters['radius'])), MAX_DISTANCE_DRIVER)
        if parameters.has_key('geometry'):
            geometry = GEOSGeometry(parameters['geometry'], srid=SRID_DEFAULT)
            poly_buffer = get_buffer_from_geometry(geometry, radius)
    except:
        pass
    return poly_buffer

def get_buffer_from_geometry(geometry, radius):
    """Get the buffer of the geometry around a radius."""
    if isinstance(geometry, LineString):
        mgeom = MultiLineString([geometry])
    else:
        mgeom = geometry
    polys = None
    for geom in mgeom:
        geom = smart_transform(geom,SRID_TRANSFORM, from_srid=SRID_DEFAULT)
        poly_buffer = geom.buffer(radius)
        if not poly_buffer.empty:
            polys = polys.union(poly_buffer) if polys else poly_buffer
    ogr = polys.ogr
    ogr.transform(SRID_DEFAULT)
    return ogr

def get_city(request):
    """Return a list of cities begining with the given value."""
    if request.method != 'POST':
        raise Http404

    query = request.POST.get('value', None)
    if query:
        cities = City.objects.filter(slug__startswith=str_slugify(query)).order_by('-population', 'slug')[:15]
    else:
        cities = []
    
    return HttpResponse('<ul>%s</ul>' % ''.join(['<li>%s</li>' % city for city in cities]))

def get_date(value, formats):
    """ Parse a date """
    for format in formats:
        try:
            return datetime.date(*time.strptime(value, format)[:3])
        except ValueError:
            continue
    return None

def get_time(value):
    """ Return a time """
    return datetime.time(value)

def _get_rank(pourcentage_rank, temporal_rank, options_rank):
    return pourcentage_rank * temporal_rank + options_rank

def sort_offers(trips, date, interval_min, interval_max, trip=None):
    dows = trip.dows if trip else None
    demand = trip.demand if trip else None

    # tuple generation, sort, reverse

    tuple_offers = [("%04d#%09d" % (
            _get_rank(
                tripo.pourcentage_rank,
                tripo.get_temporal_rank(dows, date, interval_min, interval_max),
                tripo.offer.get_options_rank(demand)
            ),
            tripo.id
        ), tripo) for tripo in trips]
    tuple_offers.sort()
    tuple_offers.reverse()

    return [item[1] for item in tuple_offers]

def sort_demands(trips, date, interval_min, interval_max, trip=None):
    dows = trip.dows if trip else None
    offer = trip.offer if trip else None

    # tuple generation, sort, reverse
    tuple_demands = [("%04d#%09d" % (
            _get_rank(
                tripd.pourcentage_rank,
                tripd.get_temporal_rank(dows, date, interval_min, interval_max),
                tripd.demand.get_options_rank(offer)
            ),
            tripd.id
        ), tripd) for tripd in trips]
    tuple_demands.sort()
    tuple_demands.reverse()

    return [item[1] for item in tuple_demands]

def get_trip_dict(trip):
    trip_dict = {
        'id': trip.id,
        'departure_city': escape(trip.departure_city),
        'departure_address': escape(trip.departure_address),
        'departure_point': trip.departure_point.wkt,
        'arrival_city': escape(trip.arrival_city),
        'arrival_address': escape(trip.arrival_address),
        'arrival_point': trip.arrival_point.wkt,
        'date': trip.date.strftime("%d/%m/%Y") if trip.date else None,
        'time': trip.time.strftime("%Hh") if trip.time else None,
        'dows': trip.print_dows(),
        'seats_available': trip.offer.driver_seats_available if trip.offer else None,
        'absolute_url': trip.get_absolute_url(),
        'user_name': trip.user.username,
        'user_id': trip.user.id,
        'mark': get_mark_average(trip.user_mark_sum, trip.user_mark_num),
    }
    return trip_dict

def get_trip_search_type(parameters):
    try:
        return int(parameters['trip_type'])
    except:
        return None

def update_trip_details_session(request, departure_point_wkt, arrival_point_wkt):
    parameters = request.REQUEST
    date = get_date(parameters['date'], FRENCH_DATE_INPUT_FORMATS)
    if date is None:
        raise Http404
    if not request.session.get('search_trip_details', None):
        # to avoid KeyError when reading session
        return date
    trip_details = request.session['search_trip_details']
    if parameters['departure_sync'] == 'true':
        trip_details['departure'].update({'name': parameters['departure_name']})
        trip_details['departure'].update({'point': departure_point_wkt})
        try:
            trip_details['departure'].update({'favoriteplace': int(parameters['departure_favoriteplace'])})
        except ValueError:
            trip_details['departure'].update({'favoriteplace': None})
    if parameters['arrival_sync'] == 'true':
        trip_details['arrival'].update({'name': parameters['arrival_name']})
        trip_details['arrival'].update({'point': arrival_point_wkt})
        try:
            trip_details['arrival'].update({'favoriteplace': int(parameters['arrival_favoriteplace'])})
        except ValueError:
            trip_details['arrival'].update({'favoriteplace': None})
    trip_details.update({'date': date.strftime("%d/%m/%Y")})
    request.session['search_trip_details'] = trip_details
    return date

def get_common_details(parameters):
    interval_min = min(abs(int(parameters['interval_min'])), MAX_INTERVAL)
    interval_max = min(abs(int(parameters['interval_max'])), MAX_INTERVAL)
    departure_point = GEOSGeometry(parameters['departure_point'], srid=SRID_DEFAULT)
    arrival_point = GEOSGeometry(parameters['arrival_point'], srid=SRID_DEFAULT)
    return interval_min, interval_max, departure_point, arrival_point

def get_trip_search_offer_details(request):
    parameters = request.REQUEST
    radius = min(abs(int(parameters['radius'])), MAX_DISTANCE_PASSENGER)
    interval_min, interval_max, departure_point, arrival_point = get_common_details(parameters)
    if departure_point is None or arrival_point is None or departure_point.geom_type != 'Point' or arrival_point.geom_type != 'Point':
        raise Http404
    date = update_trip_details_session(request, departure_point.wkt, arrival_point.wkt)
    return radius, date, interval_min, interval_max, departure_point, arrival_point

def get_trip_search_demand_details(request):
    parameters = request.REQUEST
    radius = min(abs(int(parameters['radius'])), MAX_DISTANCE_DRIVER)
    interval_min, interval_max, departure_point, arrival_point = get_common_details(parameters)
    route = GEOSGeometry(parameters['geometry'], srid=SRID_DEFAULT)
    if departure_point is None or arrival_point is None or departure_point.geom_type != 'Point' or arrival_point.geom_type != 'Point':
        raise Http404
    date = update_trip_details_session(request, departure_point.wkt, arrival_point.wkt)
    return radius, date, interval_min, interval_max, route, departure_point, arrival_point

def get_trip_search_details(request):
    parameters = request.REQUEST
    offer_radius = min(abs(int(parameters['offer_radius'])), MAX_DISTANCE_DRIVER) if parameters['offer_radius'] else None
    demand_radius = min(abs(int(parameters['demand_radius'])), MAX_DISTANCE_DRIVER) if parameters['demand_radius'] else None
    interval_min, interval_max, departure_point, arrival_point = get_common_details(parameters)
    route = GEOSGeometry(parameters['geometry'], srid=SRID_DEFAULT) if parameters['geometry'] else None
    if departure_point is None or arrival_point is None or departure_point.geom_type != 'Point' or arrival_point.geom_type != 'Point':
        raise Http404
    return offer_radius, demand_radius, interval_min, interval_max, route, departure_point, arrival_point
