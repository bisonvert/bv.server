# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""RSS Feeds"""


from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from bv.server.carpool.models import Trip, City

import time

_ABSOLUTE_URL = settings.PROJECT_ROOT_URL
if _ABSOLUTE_URL.endswith('/'):
    _ABSOLUTE_URL = _ABSOLUTE_URL.strip('/')
_RADIUS = 10000


# check the url to types.values()
types = {'from'   : 'au_depart_de',
         'to'     : 'a_destination_de',
         'results': 'resultats_annonce'}

class RSSFeed(Feed):
    description = ''
    title = u'%s, service de covoiturage - Réinventons la route' % \
        settings.PROJECT_NAME
    author_name = 'BisonVert'
    author_link = settings.PROJECT_ROOT_URL
    copyright   = u'Copyright (c) %s' % settings.PROJECT_NAME

    def get_object(self, bits):
        import pdb; pdb.set_trace()
        def default_feed():
            # all trips
            self.link = _ABSOLUTE_URL + '/annonces_covoiturage/page1/'
            self.description = u'Dernières mises à jour relatives aux'
            ' annonces de covoiturage %s.' % settings.PROJECT_NAME
            return Trip.objects.select_related().exclude_outdated().order_by(
                    '-modification_date')[:25]

        if len(bits) == 1:
            bit = bits[0]
            if bit == 'annonces_covoiturage':
                return default_feed()
            else:
                raise ObjectDoesNotExist

        elif len(bits) == 2:
            type = bits[0]
            bit = bits[1]

            if type == types['from']:
                # trips from a city
                values = bit.split('-')
                if len(values) < 2:
                    raise ObjectDoesNotExist
                try:
                    zip = int(values[-1])
                except ValueError:
                    raise ObjectDoesNotExist
                city = City.objects.get(
                        slug='-'.join(values[:-1]),
                        zipcode__gte=zip*1000,
                        zipcode__lte=(zip+1)*1000
                )
                self.link = _ABSOLUTE_URL + '/%s/%s/' % (type, bit)
                self.title += u' - Au départ de %s' % city
                self.description = (u'Dernières mises à jour relatives aux'
                u' annonces de covoiturage %s au départ de %s, dans un'
                u' rayon d\'environ %dkm.') % (settings.PROJECT_NAME,
                        city, _RADIUS/1000)
                return Trip.objects.get_trip_from_city(
                        city.point,
                        _RADIUS
                ).exclude_outdated().order_by('-modification_date')[:25]

            elif type == types['to']:
                # trips to a city
                values = bit.split('-')
                if len(values) < 2:
                    raise ObjectDoesNotExist
                try:
                    zip = int(values[-1])
                except ValueError:
                    raise ObjectDoesNotExist
                city = City.objects.get(
                        slug='-'.join(values[:-1]),
                        zipcode__gte=zip*1000,
                        zipcode__lte=(zip+1)*1000
                )
                self.link = _ABSOLUTE_URL + '/%s/%s/' % (type, bit)
                self.title += u' - A destination de %s' % city
                self.description = (u'Dernières mises à jour relatives aux'
                u' annonces de covoiturage %s à destination de %s, dans un'
                u' rayon d\'environ %dkm.') % (settings.PROJECT_NAME,
                        city, _RADIUS/1000)
                return Trip.objects.get_trip_to_city(
                        city.point,
                        _RADIUS
                ).exclude_outdated().order_by('-modification_date')[:25]

            elif type == types['results']:
                # result of a trip
                try:
                    bit = int(bit)
                except ValueError:
                    raise ObjectDoesNotExist
                trip = Trip.objects.get(pk=bit)
                self.link = _ABSOLUTE_URL + '/%s/%s/' % (type, bit)
                if trip.offer_id and not trip.demand_id:
                    trip_type = u'Offre'
                if not trip.offer_id and trip.demand_id:
                    trip_type = u'Demande'
                else:
                    trip_type = u'Indifférent'
                subject = u"%s - %s %s (%s)" % (
                    trip.departure_city,
                    trip.arrival_city,
                    trip.date.strftime("%d/%m/%Y") if not trip.regular \
                            else trip.print_dows(),
                    trip_type
                )
                self.title += u' - Annonce %s' % subject
                self.description = (u'Dernières mises à jour des annonces de'
                u' covoiturage correspondant à l\'annonce %s') % subject
                # get trips
                trips = []
                if trip.demand:
                    # is a demand
                    trip_offers = Trip.objects.get_offers(
                            trip.departure_point,
                            trip.arrival_point,
                            trip.demand.radius
                    ).exclude(pk=trip.id).exclude_outdated()
                    if settings.EXCLUDE_MY_TRIPS:
                        trip_offers = trip_offers.exclude(user=trip.user)
                    if trip.regular:
                        trip_offers = trip_offers.filter_dows(trip.dows)
                    else:
                        trip_offers = trip_offers.filter_date_interval(
                                trip.date,
                                trip.interval_min,
                                trip.interval_max
                        )
                    trip_offers = trip_offers.order_by(
                            '-modification_date')[:25]
                    trips += trip_offers
                if trip.offer:
                    # is an offer
                    trip_demands = Trip.objects.get_demands(
                            trip.offer.simple_route,
                            trip.offer.direction_route,
                            trip.offer.radius
                    ).exclude(pk=trip.id).exclude_outdated()
                    if settings.EXCLUDE_MY_TRIPS:
                        trip_demands = trip_demands.exclude(user=trip.user)
                    if trips:
                        # is is also a demand, exclude trips previously found
                        trip_demands = trip_demands.exclude(
                                id__in=[tripo.id for tripo in trips]
                        )
                    if trip.regular:
                        trip_demands = trip_demands.filter_dows(trip.dows)
                    else:
                        trip_demands = trip_demands.filter_date_interval(
                                trip.date,
                                trip.interval_min,
                                trip.interval_max
                        )
                    trip_demands = trip_demands.order_by(
                            '-modification_date')[:25]
                    trips += trip_demands
                # order trips
                tuple_trips = [(t.modification_date, t) for t in trips]
                tuple_trips.sort()
                tuple_trips.reverse()
                # return only last 25th items
                return [item[1] for item in tuple_trips][:25]

            else:
                raise ObjectDoesNotExist

        else:
            return default_feed()

    def item_link(self, obj):
        return (settings.PROJECT_ROOT_URL + obj.get_absolute_url() + '?mod=%s'
                % time.mktime(obj.modification_date.timetuple()))

    def items(self, obj):
        return obj

class AtomFeed(RSSFeed):
    feed_type = Atom1Feed
    subtitle = RSSFeed.description
