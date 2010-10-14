# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Carpool's models"""

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, LineString, MultiLineString
from django.db.models import permalink
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

from bv.server.carpool import SRID_DEFAULT, SRID_TRANSFORM, MAX_NUM_POINTS, R_CITY_ZIP
from bv.server.carpool import str_slugify, get_simple_route, get_direction_route
from bv.server.utils.models import DOWArrayField
from bv.server.utils.geodjango import smart_transform

import cPickle as pickle
import datetime

def _print_radius(value):
    """Return a radius value in km."""
    return u'%.f km' % float(value/1000.0)

class FavoritePlace(models.Model):
    """Favorite place"""
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True)
    point = models.PointField()
    design = models.CharField(max_length=200, default='default')

    def __unicode__(self):
        """Unicode representation"""
        return u"%s" % self.name

    class Meta:
        """Meta class."""
        verbose_name = _("Favorite place")
        verbose_name_plural = _("Favorite places")
        ordering = ['name']

class CityManager(models.GeoManager):
    def get_from_slug(self, slug, zipcode):
        return self.get(
            slug__iexact=slug,
            zipcode__gte=zipcode*1000,
            zipcode__lte=(zipcode+1)*1000
        )

class City(models.Model):
    """French cities."""
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    zipcode = models.PositiveIntegerField()
    point = models.PointField()
    insee_code = models.PositiveIntegerField(unique=True)
    population = models.PositiveIntegerField()

    objects = CityManager();

    def _get_zip(self):
        """Return the postal code, truncated at the appartement number"""
        return u"%02d" % (self.zipcode/1000)
    zip = property(fget=_get_zip)

    @classmethod
    def get_city(cls, value):
        """Return a city from a value"""
        if not value:
            return None
        match_address = R_CITY_ZIP.match(str_slugify(value))
        try:
            if match_address:
                return cls.objects.get_from_slug(
                        match_address.group(1),
                        int(match_address.group(2)),
                )
            else:
                return cls.objects.filter(
                    slug__startswith=str_slugify(value)
                ).order_by('-population', 'slug', 'zipcode')[0]
        except (ValueError, cls.DoesNotExist, IndexError):
            return None

    def __unicode__(self):
        """Unicode representation"""
        return u"%s (%02d)" % (self.name, self.zipcode/1000)

    class Meta:
        """Meta class"""
        verbose_name = _("City")
        ordering = ['name']

class CarType(models.Model):
    """Car types"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        """Unicode representation"""
        return u"%s" % self.name

    class Meta:
        """Meta class"""
        verbose_name = _("Car type")
        verbose_name_plural = _("Car types")
        ordering = ['name']

class TripDemand(models.Model):
    """Carpool trip demand
    
    Contains search criteria for demand

    + radius: search buit for passenger
    + optional criterias

    """
    radius = models.PositiveIntegerField(default=500) # 500m by default

    # options
    passenger_max_km_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )
    passenger_smokers_accepted = models.BooleanField(default=False)
    passenger_pets_accepted = models.BooleanField(default=False)
    passenger_place_for_luggage = models.BooleanField(default=False)
    passenger_car_type = models.ForeignKey(CarType, null=True)
    passenger_min_remaining_seats = models.PositiveIntegerField(null=True)

    def print_radius(self):
        """Return the radius, in km. Used in templates"""
        return _print_radius(self.radius)

    def get_options_rank(self, offer):
        """Compute the rank for options.
        
        Compares current object to an offer, and add one point each time an 
        option matches

        """
        if offer is None:
            return 0
        rank = 0
        # km price criterion
        if (offer.driver_km_price is not None
                and self.passenger_max_km_price is not None
                and self.passenger_max_km_price >= offer.driver_km_price):
            rank += 1
        # smoker criterion
        if offer.driver_smokers_accepted and self.passenger_smokers_accepted:
            rank += 1
        # pets criterion
        if offer.driver_pets_accepted and self.passenger_pets_accepted:
            rank += 1
        # luggage criterion
        if offer.driver_place_for_luggage and self.passenger_place_for_luggage:
            rank += 1
        # car type criterion
        if (offer.driver_car_type_id
                and self.passenger_car_type_id
                and self.passenger_car_type_id == offer.driver_car_type_id):
            rank += 1
        # seats available criterion
        if (offer.driver_seats_available is not None
                and self.passenger_min_remaining_seats is not None
                and (offer.driver_seats_available
                    <= self.passenger_min_remaining_seats)):
            rank += 1
        return rank

class TripOffer(models.Model):
    """Carpool offer.
    
    Contains search criterias for an offer.
    
    + checkpoints: aren't used for spatial search, but are saved in database to 
      allow current user to easily change his route. checkpoints are serialized
      in database
    + route: never used in queries
    + simple_route: simplified route (via geos simplify). Used in queries (via 
      it's projected version)
    + direction_route: the route, but really simplified (100 points on the
      route are picked-out. Used to check that offer and demand go to the same 
      direction.
    + radius: perimeter of the conductor search
    + optionnal criterias
    
    Not modelized:
    
    + simple_route_proj: projected version (to extended L2) of the simple_route
      (filled via a trigger)
    + direction_route_proj: projected version (to extended L2) of the 
      direction_route (filled via a trigger)
      
    """
    checkpoints = models.TextField()
    route = models.MultiLineStringField()
    # simple route for sql queries and map display
    simple_route = models.MultiLineStringField()
    # for direction calculation
    direction_route = models.LineStringField()
    radius = models.PositiveIntegerField(default=500)

    # options
    driver_km_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )
    driver_smokers_accepted = models.NullBooleanField()
    driver_pets_accepted = models.NullBooleanField()
    driver_place_for_luggage = models.NullBooleanField()
    driver_car_type = models.ForeignKey(CarType, null=True)
    driver_seats_available = models.PositiveIntegerField(null=True)

    objects = models.GeoManager()

    def __init__(self, *args, **kwargs):
        self._steps = []
        super(TripOffer, self).__init__(*args, **kwargs)

    def _get_steps(self):
        """Unserialize the check points list."""
        if self._steps:
            return self._steps
        if self.checkpoints:
            self._steps = pickle.loads(smart_str(self.checkpoints))
        return self._steps

    def _set_steps(self, value):
        """Set the check points list"""
        self._steps = value
    steps = property(
        fget=_get_steps,
        fset=_set_steps
    )

    def print_radius(self):
        """Used in templates: return the radius, in km."""
        return _print_radius(self.radius)

    def get_options_rank(self, demand):
        """Compute the option points
        
        Compare current object to a single demand. Add one point each time an 
        option match

        """
        if demand is None:
            return 0
        rank = 0
        # km price criterion
        if (demand.passenger_max_km_price is not None
                and self.driver_km_price is not None
                and demand.passenger_max_km_price >= self.driver_km_price):
            rank += 1
        # smoker criterion
        if demand.passenger_smokers_accepted and self.driver_smokers_accepted:
            rank += 1
        # pets criterion
        if demand.passenger_pets_accepted and self.driver_pets_accepted:
            rank += 1
        # luggage criterion
        if demand.passenger_place_for_luggage and self.driver_place_for_luggage:
            rank += 1
        # car type criterion
        if (demand.passenger_car_type_id
                and self.driver_car_type_id
                and (self.driver_car_type_id
                    == demand.passenger_car_type_id)):
            rank += 1
        # seats available criterion
        if (demand.passenger_min_remaining_seats is not None
                and self.driver_seats_available is not None
                and (demand.passenger_min_remaining_seats
                    <= self.driver_seats_available)):
            rank += 1
        return rank

    def save(self):
        """Save the offer.
        
        Serialize the checkpoint list, compute the simple route, the direction 
        route and call the save() method of the parent class

        """
        # dump the checkpoint list into a pickle value
        self.checkpoints = pickle.dumps(self.steps)
        # calculate a simple route for sql queries and map display
        simple_route = get_simple_route(self.route)
        if isinstance(simple_route, LineString):
            self.simple_route = MultiLineString([simple_route])
        else:
            self.simple_route = simple_route
        # calculate a simple route for direction calculation
        if simple_route.num_points <= MAX_NUM_POINTS:
            self.direction_route = get_direction_route(simple_route)
        else:
            self.direction_route = get_direction_route(self.route)
        super(TripOffer, self).save()

class TripQuerySet(models.query.QuerySet):
    """Trip queryset.
    
    Provides useful methods to query a trip efficiently
    
    """
    MAX_PERCENTAGE_RANK = 10

    def get_offers(self, departure_point, arrival_point, radius):
        """Fetch and return offer trip announces.
        
        Indifferent trips are fetched too.
        
        Entierely based on spatial criterias
        
        Search for roads close from departure or arrival points. (close is 
        defined by the radius of the offer + the radius of the demand)
        
        Return offers witch have a percentage of matching route greater than
        MAX_PERCENTAGE_RANK.
        
        Calculations are made from the simplified projected route

        """
        # rem: simple_route_proj and direction_route_proj are not modelized,
        # but are filled by a trigger
        ogr_departure = smart_transform(departure_point,SRID_TRANSFORM, from_srid=SRID_DEFAULT).ogr
        ogr_arrival = smart_transform(arrival_point,SRID_TRANSFORM, from_srid=SRID_DEFAULT).ogr
        offers = self.filter(offer__isnull=False)
        offers = offers.select_related('user', 'offer')
        return offers.extra(
            select=SortedDict([
                ('pourcentage_rank', """get_pourcentage_rank(
                    "carpool_tripoffer"."direction_route_proj",
                    ST_PointFromWKB(%s, %s),
                    ST_PointFromWKB(%s, %s)
                )
                """),
            ]),
            where=[
                """ST_DWithin(
                    "carpool_tripoffer"."simple_route_proj",
                    ST_PointFromWKB(%s, %s),
                    "carpool_tripoffer"."radius" + %s
                )
                """,
                """ST_DWithin(
                    "carpool_tripoffer"."simple_route_proj",
                    ST_PointFromWKB(%s, %s),
                    "carpool_tripoffer"."radius" + %s
                )
                """,
                """get_pourcentage_rank(
                    "carpool_tripoffer"."direction_route_proj",
                    ST_PointFromWKB(%s, %s),
                    ST_PointFromWKB(%s, %s)
                ) >= %s
                """,
            ],
            params=[
                ogr_departure.wkb, SRID_TRANSFORM,
                radius,
                ogr_arrival.wkb, SRID_TRANSFORM,
                radius,
                ogr_departure.wkb, SRID_TRANSFORM,
                ogr_arrival.wkb, SRID_TRANSFORM,
                self.MAX_PERCENTAGE_RANK,
            ],
            select_params=(
                ogr_departure.wkb, SRID_TRANSFORM,
                ogr_arrival.wkb, SRID_TRANSFORM,
            )
        )

    def get_demands(self, route, direction_route, radius):
        """Return demands trip announces.
        
        Indifferent trips are fetched too.
        
        Entirely based on spatial criterias.

        Search for roads close from departure or arrival points. (close is 
        defined by the radius of the offer + the radius of the demand)
        
        Return offers witch have a percentage of matching route greater than
        MAX_PERCENTAGE_RANK.
        
        Calculations arent made from the simplified projected route

        """
        ogr = smart_transform(route,SRID_TRANSFORM, from_srid=SRID_DEFAULT).ogr
        demands = self.filter(demand__isnull=False)
        demands = demands.select_related('user', 'demand')
        return demands.extra(
            select=SortedDict([
                ('pourcentage_rank', """get_pourcentage_rank(
                    ST_GeomFromWKB(%s, %s),
                    "carpool_trip"."departure_point",
                    "carpool_trip"."arrival_point"
                )
                """),
            ]),
            where=[
                """ST_DWithin(
                    ST_GeomFromWKB(%s, %s),
                    "carpool_trip"."departure_point_proj",
                    "carpool_tripdemand"."radius" + %s
                )
                """,
                """ST_DWithin(
                    ST_GeomFromWKB(%s, %s),
                    "carpool_trip"."arrival_point_proj",
                    "carpool_tripdemand"."radius" + %s
                )
                """,
                """get_pourcentage_rank(
                    ST_GeomFromWKB(%s, %s),
                    "carpool_trip"."departure_point",
                    "carpool_trip"."arrival_point"
                ) >= %s
                """,
            ],
            params=[
                ogr.wkb, SRID_TRANSFORM,
                radius,
                ogr.wkb, SRID_TRANSFORM,
                radius,
                direction_route.wkb, SRID_DEFAULT,
                self.MAX_PERCENTAGE_RANK,
            ],
            select_params=(direction_route.wkb, SRID_DEFAULT)
        )

    def get_mark_details(self):
        """Return the details for an user assessement.
        
        + number of assessments
        + total of the assessments marks
        
        Average is computed later

        """
        return self.extra(
            select={
                'user_mark_num': ('SELECT count(*) FROM rating_report r '
                    'WHERE r.user_id=carpool_trip.user_id'),
                'user_mark_sum': ('SELECT SUM(r.mark) FROM rating_report r '
                    'WHERE r.user_id=carpool_trip.user_id'),
            }
        )

    def exclude_outdated(self, date=None):
        """Exclude outdated anounces
        
        An announce is considered outdated if it was punctual and it's date is
        passed.

        """
        if not date:
            date = datetime.date.today()
        return self.extra(
                where = [
                    """(
                        "carpool_trip"."regular" IS False
                        AND "carpool_trip"."date"+"carpool_trip"."interval_max" >= %s
                            OR "carpool_trip"."regular" IS True
                    )
                    """,
                ],
                params = [
                    date.strftime("%Y-%m-%d"),
                ]
        )

    def filter_date_interval(self, date, interval_min, interval_max):
        """Temporal filter.
        
        Return announces matching with temporal criterias (date + intervals)
        
        If the announce is a punctual one, intervals must intersect. For this,
        we use the Postgres OVERLAPS method.
        
        If it's a regular announce, we check that at least a day of the interval
        match with the announce day-of-week selected (see the filter_dows) 
        method.
        
        This method is hardly dependent on the Postgres behavior.

        """
        str_date_min = (date-datetime.timedelta(interval_min)).strftime(
                "%Y-%m-%d")
        str_date_max = (date+datetime.timedelta(interval_max)).strftime(
                "%Y-%m-%d")
        return self.extra(
                where = [
                    """(
                        "carpool_trip"."regular" IS False
                        AND (
                            ("carpool_trip"."date"-"carpool_trip"."interval_min",
                            "carpool_trip"."date"+"carpool_trip"."interval_max")
                                OVERLAPS (DATE %s, DATE %s)
                            OR "carpool_trip"."date"-
                                "carpool_trip"."interval_min"=DATE %s
                            OR "carpool_trip"."date"+
                                "carpool_trip"."interval_max"=DATE %s
                        )
                        OR "carpool_trip"."regular" IS True
                            AND match_date_interval_dows(
                                %s, %s, %s,
                                "carpool_trip"."dows"
                            )
                    )
                    """,
                ],
                params = [
                    str_date_min, str_date_max,
                    str_date_max, str_date_min,
                    date.strftime("%Y-%m-%d"), interval_min, interval_max,
                ]
        )

    def filter_dows(self, dows):
        """Temporal Filter.
        
        Return announces matching with the Days Of Weeks given.
        
        If it's a punctual announce, at least one day match 
        with the DOWS.
        
        If it's a regular announce, at least one day from each announce match.
        
        This method is hardly dependent on the Postgres behavior.

        """
        str_dows = "{%s}" % ','.join(["%d" % dow for dow in dows])
        return self.extra(
                where = [
                    """(
                        "carpool_trip"."regular" IS True
                        AND match_dows(%s, "carpool_trip".dows)
                        OR match_date_interval_dows(
                            "carpool_trip"."date",
                            "carpool_trip"."interval_min",
                            "carpool_trip"."interval_max", %s
                        )
                    )
                    """,
                ],
                params = [
                    str_dows,
                    str_dows,
                ]
        )

    def get_trip_from_city(self, departure_point, radius):
        """Return announces originally a city with a radius parameter
        
        Don't use the route, results are just based from the departure city

        """
        ogr = smart_transform(departure_point,SRID_TRANSFORM, from_srid=SRID_DEFAULT).ogr
        return Trip.objects.select_related().extra(
            select = {
                'type': ('CASE WHEN demand_id IS NULL THEN 0 '
                    'WHEN offer_id IS NULL THEN 1 ELSE 2 END'),
            },
            where = [
                ('ST_DWithin(ST_PointFromWKB(%s, %s), '
                    '"carpool_trip"."departure_point_proj", %s)'),
            ],
            params = [
                ogr.wkb, SRID_TRANSFORM,
                radius,
            ],
        )

    def get_trip_to_city(self, arrival_point, radius):
        """Return announces bounds to a city, with a radius parameter
        
        Don't use route, results are just based from the arrival city

        """
        ogr = smart_transform(arrival_point,SRID_TRANSFORM, from_srid=SRID_DEFAULT).ogr
        return Trip.objects.select_related().extra(
            select = {
                'type': ('CASE WHEN demand_id IS NULL THEN 0 '
                    'WHEN offer_id IS NULL THEN 1 ELSE 2 END')
            },
            where = [
                'ST_DWithin(ST_PointFromWKB(%s, %s), '
                '"carpool_trip"."arrival_point_proj", %s)',
            ],
            params = [
                ogr.wkb, SRID_TRANSFORM,
                radius,
            ]
        )

class TripManager(models.GeoManager):
    """Manager for Trip objects"""
    
    def get_query_set(self):
        """Return the queryset used for Trip."""
        model = models.get_model('carpool', 'Trip')
        return TripQuerySet(model)

    def __getattr__(self, attr, *args):
        """To chain methods directly in the manager.
        http://www.djangosnippets.org/snippets/562/
        
        """
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class Trip(models.Model):
    """Carpool Trip announce
    
    + name: announce name. Be careful, and take this name private. It must NOT
      be communicated to other users. Nobody wants that all other users knows 
      that the trip is named "Week end with Gran'ma" !
    + user: Owner of the trip announce
    + departure_city
    + departure_address
    + departure_point
    + arrival_city
    + arrival_address
    + arrival_point
    + offer: related carpool offer
    + demand: related carpool demand
    
    Temporal criterias:

    + regular: is the traject regular or punctual
    + date: departure date, if one
    + interval_min: nomber of interval (days) accepted before the departure date
    + interval_max: nomber of interval (days) accepted after the departure date
    + dows (DowArray): days of week
    + time (Time): departure time

    Options:

    + comment (Text): commentaire.
    + alert (Boolean): alerte email activée ou non.

    Informations complémentaires:

    + creation_date
    + modification_date

    """
    OFFER = 0
    DEMAND = 1
    BOTH = 2

    TYPE_CHOICES = (
        (OFFER, OFFER),
        (DEMAND, DEMAND),
        (BOTH, BOTH),
    )

    FROM = 1
    TO = 2

    DOWS = (
        (1, _("Mo")),
        (2, _("Tu")),
        (3, _("We")),
        (4, _("Th")),
        (5, _("Fr")),
        (6, _("Sa")),
        (0, _("Su")),
    )

    name = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    departure_city = models.CharField(max_length=200)
    departure_address = models.CharField(max_length=200)
    departure_point = models.PointField()
    arrival_city = models.CharField(max_length=200)
    arrival_address = models.CharField(max_length=200)
    arrival_point = models.PointField()
    offer = models.ForeignKey(TripOffer, null=True)
    demand = models.ForeignKey(TripDemand, null=True)

    # date params
    regular = models.BooleanField(default=False)
    date = models.DateField(null=True)
    interval_min = models.PositiveIntegerField(default=0)
    interval_max = models.PositiveIntegerField(default=0)
    dows = DOWArrayField(default=[])
    time = models.TimeField(null=True)

    # options
    comment = models.CharField(max_length=300)
    alert = models.BooleanField(default=False)

    # object dates
    creation_date = models.DateTimeField(auto_now_add=True, auto_now=True)
    modification_date = models.DateTimeField(auto_now_add=True, auto_now=True)

    objects = TripManager()

    def __init__(self, *args, **kwargs):
        """Initialize the radius and the type of the announce."""
        self._trip_type = None
        self._trip_radius = None
        super(Trip, self).__init__(*args, **kwargs)

    def _get_type(self):
        """return the announce type (offer, demand, indifferent)"""
        if self.offer and self.demand:
            return self.BOTH
        elif self.offer:
            return self.OFFER
        elif self.demand:
            return self.DEMAND
        elif self._trip_type is not None:
            return self._trip_type
        return None
    def _set_type(self, trip_type):
        """set the announce type"""
        self._trip_type = trip_type
    trip_type = property(fget=_get_type, fset=_set_type)

    def _get_radius(self):
        """Return the radius"""
        return self._trip_radius
    def _set_radius(self, trip_radius):
        """Set the radius"""
        self._trip_radius = trip_radius
    trip_radius = property(fget=_get_radius, fset=_set_radius)

    def get_offer_radius(self):
        """Return the offer radius"""
        if self.offer:
            return self.offer.radius
        elif self.trip_type == self.OFFER:
            return self.trip_radius
        return None
    def print_offer_radius(self):
        """Return the offer radius, in km"""
        return _print_radius(self.get_offer_radius())

    def get_demand_radius(self):
        """Return the demand radius"""
        if self.demand:
            return self.demand.radius
        elif self.trip_type == self.DEMAND:
            return self.trip_radius
        return None
    def print_demand_radius(self):
        """Return the demand radius, in km"""
        return _print_radius(self.get_demand_radius())

    def print_dows(self):
        """return the unicode representation for days of weeks"""
        return u'-'.join([value for (key, value) in self.DOWS
            if key in self.dows])

    def get_temporal_rank(self, dows=None, date=None, interval_min=0,
            interval_max=0):
        """Compute a temporal mark for an announce

        Compares the current object to the given parameters, and affect a mark, 
        from 0 to 9. 9 being the best match.
        
        Here is the different attribuable marks:
        
        For regular trip announces:
        
        + 2: We match with existing DOWs (not really interesting for the driver) 
        + 3: A DOW is missing within the annouce.
        + 8: Our days of weeks are inside the announce DOWs (exemple: we are  
            seeking for a route for Mo, Tue, Wed and the annouce is for Mo, Tue, 
            Wed, Thu
        + 9: All DOWs are matching
        
        For punctual ones:
        
        + 1: We are matching with DOWs (not really interesting)
        + 9: Dates matches exactly
        + 7: Date of the search is into the temporary interval of the announce
        + 4: Announce date is in the temporal interval, but search date isn't in
            the temporal interval
        + 0: Only intervals overlaps

        """
        # we should have date xor dows
        if self.regular:
            # dows
            if date is not None:
                # date vs dows
                return 2
            if dows is not None:
                # dows vs dows
                if dows == self.dows:
                    return 9
                else:
                    # check if self.dows contains dows
                    for dow in dows:
                        if dow not in self.dows:
                            return 3
                    return 8
        else:
            # date
            if date is not None:
                # date vs date
                if date == self.date:
                    return 9
                elif (date >= self.date-datetime.timedelta(self.interval_min)
                        and (date <=
                            self.date+datetime.timedelta(self.interval_max))):
                    return 7
                elif (self.date >= date-datetime.timedelta(interval_min)
                        and (self.date <=
                            date+datetime.timedelta(interval_max))):
                    return 4
                return 0
            if dows is not None:
                # dows vs date
                return 1

    def get_public_name(self):
        """Return a public name for the trip.
        
        In the form of: Departure City - Arrival City Date/DOWs

        """
        return u"%s - %s %s" % (
            self.departure_city,
            self.arrival_city,
            (self.date.strftime("%d/%m/%Y")
                    if not self.regular
                    else self.print_dows())
        )

    def delete(self):
        """Deletes matching demand and offers.
        
        Call the delete() method of the parent class

        """
        if self.offer:
            self.offer.delete()
        if self.demand:
            self.demand.delete()
        super(Trip, self).delete()

    @permalink
    def get_absolute_url(self):
        """Build the announce URL."""
        if self.regular:
            return ('carpool:ajax_get_trip_details_regular', [
                '-'.join([value
                    for (key, value) in self.DOWS
                    if key in self.dows]),
                str_slugify(self.departure_city),
                str_slugify(self.arrival_city),
                str(self.id)
            ])
        else:
            return ('carpool:ajax_get_trip_details_punctual', [
                self.date.strftime("%d-%m-%Y"),
                str_slugify(self.departure_city),
                str_slugify(self.arrival_city),
                str(self.id)
            ])

    def __unicode__(self):
        """Unicode representation of a Trip."""
        return u"%s - %s" % (self.user.username, self.name)
