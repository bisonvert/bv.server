# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

""" Views for the carpool app."""

from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.gis.geos import MultiPoint, GEOSGeometry
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.utils import simplejson

from django.contrib.auth.decorators import login_required
from bv.server.carpool import MAX_DISTANCE_DRIVER, MAX_DISTANCE_PASSENGER, \
    MAX_INTERVAL, R_CITY_ZIP, get_direction_route, str_slugify
from bv.server.carpool.forms import SearchTripForm, SearchTripWithDatesForm, \
    ChooseDepartArrivalCityForm, EditTripOfferOptionsForm, \
    EditTripDemandOptionsForm, EditTripForm

from bv.server.carpool.models import City, FavoritePlace, Trip, TripDemand, TripOffer
from bv.server.carpool.misc import get_mark_average, get_date, get_trip_search_details, \
    get_trip_dict, get_trip_search_type, get_trip_search_offer_details, \
    get_trip_search_demand_details, sort_offers, sort_demands

from utils.fields import FRENCH_DATE_INPUT_FORMATS
from utils.paginator import PaginatorRender

from lib import LibCarpool
import datetime

_TRIP_PG = [25, 50, 100]
_MYTRIP_PG = [10, 20, 50]
_LAYOUTS = ['rmll2008', 'iframe', 'specific']
_MAX_TRIP = 30

def home(request, layout=None, theme_id=None, theme_dict=None, format_id=None, \
        format_dict=None, media_specific=None, date=None, departure=None, \
        arrival=None):
    """Home.
    
    This view is acessible via GET and POST.
    
    
    On GET, it displays a form for selecting a trip
    On POST, check if the form is valid, and redirect to other views
    """
    
    def get_dates_available(dates):
        """Filter dates from a set of given dates
        
        filter dates in past
        
        """
        today = datetime.date.today()
        return [date for date in dates if date[0] >= today]

    if media_specific is None:
        media_specific = ''

    response_dict = {
        'current_item': 1,
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'theme_id': theme_id,
        'theme_dict': theme_dict,
        'format_id': format_id,
        'format_dict': format_dict,
        'departure': departure,
        'arrival': arrival,
    }

    today = datetime.date.today()
    dates_available = () 

    search_trip_details = request.session.get('search_trip_details', None)
    if search_trip_details and not theme_id:
        date = get_date(search_trip_details['date'], FRENCH_DATE_INPUT_FORMATS)
        if date is not None and dates_available:
            # check if date in session is in dates_available, else it would print an error
            if date not in dates_available:
                date = None
        initial = {
            'departure': search_trip_details['departure']['name'],
            'departure_point': search_trip_details['departure']['point'],
            'departure_favoriteplace': search_trip_details['departure']['favoriteplace'] if 'favoriteplace' in search_trip_details['departure'] else None,
            'arrival': search_trip_details['arrival']['name'],
            'arrival_point': search_trip_details['arrival']['point'],
            'arrival_favoriteplace': search_trip_details['arrival']['favoriteplace'] if 'favoriteplace' in search_trip_details['arrival'] else None,
            'date': date,
            'type': Trip.OFFER,
        }
    elif theme_id:
        initial = {
            'date': date,
            'departure': departure,
            'arrival': arrival,
        }
    else:
        initial = {'date': today}

    if request.method == 'POST':
        if dates_available:
            form = SearchTripWithDatesForm(dates_available, data=request.POST)
        else:
            form = SearchTripForm(data=request.POST)
        if form.is_valid():
            try:
                trip_type = int(form.cleaned_data['type'])
            except:
                trip_type = Trip.OFFER
            search_trip_details = {
                'departure': {'name': form.cleaned_data['departure'], 'point': form.cleaned_data['departure_point'], 'favoriteplace': form.cleaned_data['departure_favoriteplace']},
                'arrival': {'name': form.cleaned_data['arrival'], 'point': form.cleaned_data['arrival_point'], 'favoriteplace': form.cleaned_data['arrival_favoriteplace']},
                'date': form.cleaned_data['date'].strftime("%d/%m/%Y") if form.cleaned_data['date'] else today.strftime("%d/%m/%Y")
            }
            request.session['search_trip_details'] = search_trip_details
            match_departure = R_CITY_ZIP.match(str_slugify(form.cleaned_data['departure']))
            match_arrival = R_CITY_ZIP.match(str_slugify(form.cleaned_data['arrival']))
            args = None
            if match_departure and match_arrival:
                args = [match_departure.group(1), match_departure.group(2), match_arrival.group(1), match_arrival.group(2)]

            if trip_type == Trip.OFFER:
                if args:
                    return HttpResponseRedirect(reverse('carpool:robots_search_offer_trip', args=args))
                else:
                    return HttpResponseRedirect(reverse('carpool:search_offer_trip'))
            else:
                if args:
                    return HttpResponseRedirect(reverse('carpool:robots_search_demand_trip', args=args))
                else:
                    return HttpResponseRedirect(reverse('carpool:search_demand_trip'))

    elif request.method == "GET":
        if dates_available:
            form = SearchTripWithDatesForm(dates_available, initial=data)
        else:
            initial_data = {'date': today}
            form = SearchTripForm(initial=initial_data)
            
    response_dict.update({
        'form': form,
        'date_uptodate': dates_available,
    })
    
    # theming
    if layout in _LAYOUTS:
        template = loader.get_template('carpool/tools/%s_form.html' % layout)
    else:
        template = loader.get_template('carpool/home.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def robots_search_trip(request, departure_slug, departure_zip, arrival_slug, arrival_zip, trip_type):
    """Search for a trip, and put information in session
    
    Then, call and return the response of the "search_trip" view
    
    """
    try:
        int_departure_zip = int(departure_zip)
        int_arrival_zip = int(arrival_zip)
        departure_city = City.objects.get(slug=str_slugify(departure_slug), zipcode__gte=int_departure_zip*1000, zipcode__lte=(int_departure_zip+1)*1000)
        arrival_city = City.objects.get(slug=str_slugify(arrival_slug), zipcode__gte=int_arrival_zip*1000, zipcode__lte=(int_arrival_zip+1)*1000)
        search_trip_details = {
            'departure': {'name': smart_unicode(departure_city), 'point': departure_city.point.wkt, 'favoriteplace': None},
            'arrival': {'name': smart_unicode(arrival_city), 'point': arrival_city.point.wkt, 'favoriteplace': None},
        }
        if request.session.get('search_trip_details'):
            if smart_unicode(departure_city) != request.session['search_trip_details']['departure']['name'] or smart_unicode(arrival_city) != request.session['search_trip_details']['arrival']['name']:
                request.session['search_trip_details'].update(search_trip_details)
        else:
            request.session['search_trip_details'] = search_trip_details
            request.session['search_trip_details'].update({'date': datetime.date.today().strftime("%d/%m/%Y")})
    except City.DoesNotExist:
        pass
    return search_trip(request, trip_type)

def search_trip(request, trip_type):
    """Search for a trip
    
    Get information on the trip from session, and request the model to fetch
    departure and arrival points.
    
    If there is no information in session, nor proposed adresses aren't found
    in database, redirect the user to the homepage.
    
    """
    # check session
    search_trip_details = request.session.get('search_trip_details', None)
    if not search_trip_details:
        return HttpResponseRedirect(reverse('carpool:home'))

    try:
        mpoints = MultiPoint([GEOSGeometry(search_trip_details['departure']['point']), 
                GEOSGeometry(search_trip_details['arrival']['point'])])
    except:
        return HttpResponseRedirect(reverse('carpool:home'))

    response_dict = {
        'current_item': 1,
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'geometry': mpoints.envelope.wkt,
        'trip_details': search_trip_details,
        'trip_type': trip_type,
        'places': FavoritePlace.objects.filter(design=settings.THEME_USED).order_by('name'),
        'OFFER': Trip.OFFER,
    }

    template = loader.get_template('carpool/search_trip.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

# TODO: Use Piston API
def get_trips(request):
    """Get (JSON formatted) informations about all trips (offer or demand)

    """
    trip_search_type = get_trip_search_type(request.REQUEST)
    
    params = {
        'is_offer': trip_search_type == Trip.DEMAND,
        'is_demand': trip_search_type == Trip.OFFER,
    }
    
    if trip_search_type == Trip.OFFER:
        # search for offers
        (offer_radius, date, interval_min, interval_max, departure_point,
            arrival_point) = get_trip_search_offer_details(request)
        params['offer_radius'] = offer_radius
            
    elif trip_search_type == Trip.DEMAND:
        #search for demands
        (demand_radius, date, interval_min, interval_max, route, departure_point,
            arrival_point) = get_trip_search_demand_details(request)
        params['demand_radius'] = demand_radius
        params['route'] = route
        
    params['date'] = date
    params['interval_min'] = interval_min
    params['interval_max'] = interval_max
    params['departure_point'] = departure_point
    params['arrival_point'] = arrival_point

    lib = LibCarpool()
    results = lib.get_trip_results(**params)
    trip_demands = results['trip_demands']
    trip_offers = results['trip_offers']
    trip = results['trip']
    

    if trip_search_type == Trip.OFFER:
        trips = trip_offers
    else:
        trips = trip_demands

    response_dict = {
        'authenticated': request.user.is_authenticated(),
        'trips': [get_trip_dict(t) for t in trips],
    }

    resp = HttpResponse()
    simplejson.dump(response_dict , resp, ensure_ascii=False, separators=(',',':'))
    return resp

def trip_list(request, page):
    """Return a paginated list of all requested trips

    """
    ordering = {
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
    }
    pg = _TRIP_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _TRIP_PG:
                pg = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pg
    get_url = '?pg=%d&order=%s' % (pg, order)

    oargs = ordering[order]

    paginator = PaginatorRender(
        Trip.objects.exclude_outdated().extra(select={'type': 'CASE WHEN demand_id IS NULL THEN 0 WHEN offer_id IS NULL THEN 1 ELSE 2 END'}).order_by(*oargs),
        page,
        pg,
        allow_empty_first_page=True,
        extra_context = {
            'paginations': _TRIP_PG,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
            'order': order,
        }
    )
    return paginator.render(request, 'carpool/trip_list.html')

def choose_depart_from_arrival_to(request):
    """Display a form to select a city to go from or to go to.
    
    This view can be processed with both GET and POST requests.
    
    On GET, displays a form to enter data; On POST, process the data and
    redirect to arrival_to or depart_from views.
    
    """
    if request.method == 'POST':
        form = ChooseDepartArrivalCityForm(request.POST)
        if form.is_valid():
            form.cleaned_data['depart_arrival']
            if int(form.cleaned_data['depart_arrival']) == Trip.FROM:
                return HttpResponseRedirect(reverse(
                    'carpool:show_departure_from',
                    args=[form.city_obj.slug, form.city_obj.zip, 1])
                )
            else:
                return HttpResponseRedirect(reverse(
                    'carpool:show_arrival_to',
                    args=[form.city_obj.slug, form.city_obj.zip, 1])
                )
    else:
        form = ChooseDepartArrivalCityForm()

    response_dict = {
        'form': form
    }

    template = loader.get_template('carpool/choose_depart_from_arrival_to.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def depart_from_arrival_to(request, city_slug, city_zip, is_depart, page):
    """Displays the list of trip offers with a departure or an arrival from or to
    the given city
    
    """
    ordering = {
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
    }
    pg = _TRIP_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _TRIP_PG:
                pg = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pg
    get_url = '?pg=%d&order=%s' % (pg, order)

    oargs = ordering[order]
    
    radius = 10000
    int_city_zip = int(city_zip)
    city = get_object_or_404(
            City, slug=str_slugify(city_slug),
            zipcode__gte=int_city_zip*1000,
            zipcode__lte=(int_city_zip+1)*1000
    )

    if is_depart:
        trips = Trip.objects.get_trip_from_city(city.point, radius).exclude_outdated().order_by(*oargs)
    else:
        trips = Trip.objects.get_trip_to_city(city.point, radius).exclude_outdated().order_by(*oargs)

    paginator = PaginatorRender(
        trips,
        page,
        pg,
        allow_empty_first_page=True,
        extra_context = {
            'city': city,
            'is_depart': is_depart,
            'paginations': _TRIP_PG,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
            'order': order,
        }
    )
    return paginator.render(request, 'carpool/depart_from_arrival_to.html')

def depart_from(request, departure_slug, departure_zip, page):
    """Alias to depart_from_arrival_to view
    
    """
    return depart_from_arrival_to(request, departure_slug, departure_zip, True, page)

def arrival_to(request, arrival_slug, arrival_zip, page):
    """Alias to depart_from_arrival_to view
    
    """
    return depart_from_arrival_to(request, arrival_slug, arrival_zip, False, page)

@login_required
def my_trips(request, page=1):
    """Return a paginated list of trips for the logged user
    
    """
    ordering = {
        'name': ['name'],
        '-name': ['-name'],
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
    pg = _MYTRIP_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _MYTRIP_PG:
                pg = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pg
    get_url = '?pg=%d&order=%s' % (pg, order)

    oargs = ordering[order]

    paginator = PaginatorRender(
        request.user.trip_set.all().extra(select={'type': 'CASE WHEN demand_id IS NULL THEN 0 WHEN offer_id IS NULL THEN 1 ELSE 2 END'}).order_by(*oargs),
        page,
        pg,
        allow_empty_first_page=True,
        extra_context = {
            'current_item': 10,
            'paginations': _MYTRIP_PG,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
            'order': order,
        }
    )
    return paginator.render(request, 'carpool/my_trips.html')

@login_required
def add_trip_from_search(request):
    """Add a trip from a previous search (stored in session)
    
    """
    def _get_favorite_place(json, key):
        try:
            favorite_place_id = int(json.get(key).get('favoriteplace'))
            return FavoritePlace.objects.get(pk=favorite_place_id)
        except (ValueError, FavoritePlace.DoesNotExist):
            return None

    if request.method != 'POST' or 'trip_details' not in request.POST:
        return HttpResponseRedirect('carpool:add_trip')

    trip = Trip(user=request.user)

    try:
        json = simplejson.loads(request.POST['trip_details'])
        trip.trip_type = int(json.get('type'))
        trip.trip_radius = int(json.get('radius'))
        departure_favoriteplace = _get_favorite_place(json, 'departure')
        if departure_favoriteplace:
            trip.departure_city = departure_favoriteplace.city
            trip.departure_address = departure_favoriteplace.address
            trip.departure_point = departure_favoriteplace.point
        else:
            trip.departure_city = json.get('departure').get('city')
            trip.departure_point = GEOSGeometry(json.get('departure').get('point'))
        arrival_favoriteplace = _get_favorite_place(json, 'arrival')
        if arrival_favoriteplace:
            trip.arrival_city = arrival_favoriteplace.city
            trip.arrival_address = arrival_favoriteplace.address
            trip.arrival_point = arrival_favoriteplace.point
        else:
            trip.arrival_city = json.get('arrival').get('city')
            trip.arrival_point = GEOSGeometry(json.get('arrival').get('point'))
        trip.interval_min = min(abs(int(json.get('interval_min_radius'))), MAX_INTERVAL)
        trip.interval_max = min(abs(int(json.get('interval_max_radius'))), MAX_INTERVAL)
        trip.date = get_date(json.get('date'), FRENCH_DATE_INPUT_FORMATS)
        form = AddModifyTripOptionsForm(initial=model_to_dict(request.user.get_profile()), instance=trip)
    except:
        return HttpResponseRedirect(reverse('carpool:add_trip'))

    mpoints = MultiPoint([trip.departure_point, trip.arrival_point])
    response_dict = {
        'current_item': 10,
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'trip': trip,
        'form': form,
        'geometry': mpoints.envelope.wkt,
        'trip_from_search': True,
        'hours': range(24),
    }

    template = loader.get_template('carpool/add_modify_trip.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def add_return_trip(request, trip_id):
    """Create a new back trip based on information of an existing trip
    
    """                   
                    
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)
    new_trip = Trip(user=request.user)
    new_trip.name = _('%(trip_name)s - Return') % {'trip_name': trip.name}
    new_trip.trip_type = trip.trip_type
    new_trip.departure_city = trip.arrival_city
    new_trip.departure_address = trip.arrival_address
    new_trip.departure_point = trip.arrival_point
    new_trip.arrival_city = trip.departure_city
    new_trip.arrival_address = trip.departure_address
    new_trip.arrival_point = trip.departure_point
    new_trip.regular = trip.regular
    if new_trip.regular:
        new_trip.dows = trip.dows

    new_offer = None
    if trip.offer:
        new_offer = TripOffer()
        new_offer.checkpointlist = trip.offer.checkpointlist
        new_offer.checkpointlist.reverse()
        new_offer.radius = trip.offer.radius
        new_trip.offer = new_offer

    new_demand = None
    if trip.demand:
        new_demand = TripDemand()
        new_demand.radius = trip.demand.radius
        new_trip.demand = new_demand

    userprofiledata = model_to_dict(request.user.get_profile())
        
    form_trip = EditTripForm(initial=userprofiledata, instance=new_trip)
    form_offer = EditTripOfferOptionsForm(initial=userprofiledata, 
        instance=new_offer, prefix='offer')
    form_demand = EditTripDemandOptionsForm(initial=userprofiledata, 
        instance=new_demand, prefix='demand')

    points = [cp['point'] for cp in trip.offer.checkpointlist] if trip.offer else []
    points.append(trip.departure_point)
    points.append(trip.arrival_point)
    mpoints = MultiPoint(points)    

    response_dict = {
        'form_trip': form_trip,
        'form_offer_options': form_offer,
        'form_demand_options': form_demand,
        'default_center': settings.DEFAULT_MAP_CENTER_POINT,
        'default_zoom': settings.DEFAULT_MAP_CENTER_ZOOM,
        'return_trip': True,
    }

    template = loader.get_template('carpool/add_modify_trip.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def add_modify_trip(request, trip_id=None):
    """Add or modify an existing trip.
    
    If a trip id is specified, retreive it and edit it (save it if needed)
    If no trip id is specified, create a new new trip and process it.
    
    """
    if request.method == 'POST':
        if trip_id:
            trip = get_object_or_404(Trip, id=trip_id, user=request.user)
            form_offer = EditTripOfferOptionsForm(data=request.POST, 
                instance=trip.offer, prefix="offer")
            form_demand = EditTripDemandOptionsForm(data=request.POST, 
                instance=trip.demand, prefix="demand")
        else:
            trip = Trip(user=request.user)
            form_offer = EditTripOfferOptionsForm(data=request.POST, 
                prefix="offer")
            form_demand = EditTripDemandOptionsForm(data=request.POST,
                prefix="demand")
 
        form_trip = EditTripForm(data=request.POST, instance=trip)
        error = False
        if form_trip.is_valid():
            trip_type = int(form_trip['trip_type'].data)
            trip = form_trip.save(commit=False)
            
            if trip_type != Trip.DEMAND : 
                if form_offer.is_valid():
                    trip.offer = form_offer.save()
                else:
                    error = True
                
            if trip_type != Trip.OFFER:
                if form_demand.is_valid():
                    trip.demand = form_demand.save()
                else:
                    error = True
            
            # if we have an offer, and a demand is already registred, delete it 
            if trip_type == Trip.OFFER and trip.demand is not None: 
                trip.demand.delete()
                trip.demand = None 
            
            # if we have a demand, and an offer is already registred, delete it   
            if trip_type == Trip.DEMAND and trip.offer is not None: 
                trip.offer.delete()
                trip.offer = None 
            if error ==False:
                trip.save()
                if request.POST['return_trip'] == 'true':
                    return HttpResponseRedirect(reverse('carpool:add_return_trip', args=[trip.id]))
                else:
                    return HttpResponseRedirect(reverse('carpool:show_trip_results', args=[trip.id]))
    
    # request.method = "GET"
    else:
        # request user preferences
        userprofiledata = model_to_dict(request.user.get_profile())

        form_trip = EditTripForm(initial=userprofiledata)
        form_offer = EditTripOfferOptionsForm(initial=userprofiledata, prefix="offer")
        form_demand = EditTripDemandOptionsForm(initial=userprofiledata, prefix="demand")
        
        if trip_id:
            trip = get_object_or_404(Trip,id=trip_id, user=request.user)
            form_trip = EditTripForm(instance=trip)
            if trip.offer:
                form_offer = EditTripOfferOptionsForm(instance=trip.offer, 
                    prefix="offer")
            if trip.demand:
                form_demand = EditTripDemandOptionsForm(instance=trip.demand, 
                    prefix="demand")
    
    response_dict = {
        'form_trip': form_trip,
        'form_offer_options': form_offer,
        'form_demand_options': form_demand,
        'default_center': settings.DEFAULT_MAP_CENTER_POINT,
        'default_zoom': settings.DEFAULT_MAP_CENTER_ZOOM     
    }

    template = loader.get_template('carpool/add_modify_trip.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def trip_results(request, trip_id):
    """Show the results for an existing Trip.
    
    """
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)

    if request.method == 'POST':
        if request.POST.has_key('trip_details'):
            try:
                json = simplejson.loads(request.POST['trip_details'])
                if trip.offer:
                    route = json.get('route')
                    checkpoints = []
                    for step in json.get('steps', []):
                        checkpoint = {
                            'point': GEOSGeometry(step.get('point')),
                        }
                        checkpoints.append(checkpoint)
                trip.departure_point = GEOSGeometry(json.get('departure').get('point'))
                trip.arrival_point = GEOSGeometry(json.get('arrival').get('point'))
                trip.interval_min = min(abs(int(json.get('interval_min_radius'))), MAX_INTERVAL)
                trip.interval_max = min(abs(int(json.get('interval_max_radius'))), MAX_INTERVAL)
                if trip.offer:
                    trip.offer.checkpointlist = checkpoints
                    trip.offer.route = GEOSGeometry(route)
                    trip.offer.radius = min(abs(int(json.get('offer_radius'))), MAX_DISTANCE_DRIVER)
                    trip.offer.save()
                if trip.demand:
                    trip.demand.radius = min(abs(int(json.get('demand_radius'))), MAX_DISTANCE_PASSENGER)
                    trip.demand.save()
                trip.save()
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()
                return HttpResponseRedirect(reverse('carpool:list_user_trips', args=[1]))

    response_dict = {
        'current_item': 10,
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'geometry': trip.offer.route.envelope.wkt if trip.offer else MultiPoint(trip.departure_point, trip.arrival_point).envelope.wkt,
        'trip': trip,
    }

    template = loader.get_template('carpool/trip_results.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def get_trip_results(request, trip_id):
    """Display results for a trip.   

    """
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)

    #get the trip search details
    (offer_radius, demand_radius, interval_min, interval_max, route,
        departure_point, arrival_point) = get_trip_search_details(request)
        
    if trip.offer and (route is None or route.geom_type != 'MultiLineString'):
        raise Http404

    today = datetime.date.today()

    if trip.demand:
        trip_offers = Trip.objects.get_offers(departure_point, arrival_point, demand_radius).exclude(pk=trip.id)
        trip_offers = trip_offers.get_mark_details()
        
        if trip.regular:
            trip_offers = trip_offers.filter_dows(trip.dows)
        else:
            trip_offers = trip_offers.filter_date_interval(trip.date, interval_min, interval_max)
        trip_offers = trip_offers.exclude_outdated(today)
        # exclude my trips ?
        if settings.EXCLUDE_MY_TRIPS:
            trip_offers = trip_offers.exclude(user=request.user)
        # ordering and limit
        trip_offers = trip_offers.order_by('-pourcentage_rank')[:_MAX_TRIP]
        trip_offers = sort_offers(trip_offers, trip.date, interval_min, interval_max, trip=trip)

    if trip.offer:
        trip_demands = Trip.objects.get_demands(route, get_direction_route(route), offer_radius).exclude(pk=trip.id)
        trip_demands = trip_demands.get_mark_details()
        if trip.regular:
            trip_demands = trip_demands.filter_dows(trip.dows)
        else:
            trip_demands = trip_demands.filter_date_interval(trip.date, interval_min, interval_max)
        trip_demands = trip_demands.exclude_outdated(today)
        # exclude my trips ?
        if settings.EXCLUDE_MY_TRIPS:
            trip_demands = trip_demands.exclude(user=request.user)
        # ordering and limit
        trip_demands = trip_demands.order_by('-pourcentage_rank')[:_MAX_TRIP]
        trip_demands = sort_demands(trip_demands, trip.date, interval_min, interval_max, trip=trip)

    response_dict = {
        'authenticated': request.user.is_authenticated(),
        'trip_offers': [get_trip_dict(t) for t in trip_offers] if trip.demand else None,
        'trip_demands': [get_trip_dict(t) for t in trip_demands] if trip.offer else None,
    }

    resp = HttpResponse()
    simplejson.dump(response_dict , resp, ensure_ascii=False, separators=(',',':'))
    return resp

@transaction.commit_on_success
@login_required
def delete_trip(request, trip_id):
    """Delete an existing trip
    
    """
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)

    if trip.talk_set.all():
        return HttpResponseRedirect(reverse('talks:delete_trip', args=[trip.id]))

    trip.delete()
    return HttpResponseRedirect(reverse('carpool:list_user_trips', args=[1]))

@login_required
def switch_alert(request, trip_id):
    """Switch alert notifications
    
    """
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)
    trip.alert = not trip.alert
    trip.save(update_modification_date=False)
    response_dict = {'status': 'ok', 'alert': trip.alert}
    resp = HttpResponse()
    simplejson.dump(response_dict , resp, ensure_ascii=False, separators=(',',':'))
    return resp

def trip_details(request, trip_id):
    """Return trip details of a specified trip

    """
    trip = get_object_or_404(Trip.objects.get_mark_details(), pk=trip_id)

    response_dict = {
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'geometry': trip.offer.route.envelope.wkt if trip.offer else MultiPoint(trip.departure_point, trip.arrival_point).envelope.wkt,
        'trip': trip,
        'user_mark': get_mark_average(trip.user_mark_sum, trip.user_mark_num),
    }

    template = loader.get_template('carpool/trip_details.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))
