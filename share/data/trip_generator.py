# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from django.utils.encoding import smart_unicode
from htmlentitydefs import name2codepoint as n2cp

from bv.server.carpool.models import City, Trip, TripOffer, TripDemand

import simplejson
import random
import datetime
import re

ROUTE_PATH = '/home/zebuline/'
ROUTE_FILE = 'routes.txt'

#USER_CHOICE = [2, 23, 24]
USER_CHOICE = [23, 24]
OFFER_RADIUS_CHOICE = [500, 1000, 2000, 5000, 10000, 15000, 20000]
DEMAND_RADIUS_CHOICE = [500, 1000, 2000, 5000, 10000, 15000, 20000]

route_file = open("%s%s" % (ROUTE_PATH, ROUTE_FILE), mode= 'r')

today = datetime.date.today()

def decode_htmlentities(string):
    def substitute_entity(match):
        ent = match.group(2)
        if match.group(1) == "#":
            return unichr(int(ent))
        else:
            cp = n2cp.get(ent)
            if cp:
                return unichr(cp)
            else:
                return match.group()
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

# offer creation
try:
    index = 0
    for line in route_file:
        index += 1
        try:
            json = simplejson.loads(line)
            trip_type = random.choice([0, 1, 2])
            user = User.objects.get(pk=random.choice(USER_CHOICE))
            regular = random.choice([True, False])
            departure_city = decode_htmlentities(smart_unicode(json.get('departure_name')[0]))
            arrival_city = decode_htmlentities(smart_unicode(json.get('arrival_name')[0]))
            print departure_city, arrival_city, trip_type, user.username, regular
            trip = Trip(
                name=u"%s - %s" % (departure_city, arrival_city),
                user=user,
                departure_city=departure_city,
                departure_point=GEOSGeometry(json.get('departure_point')[0]),
                arrival_city=arrival_city,
                arrival_point=GEOSGeometry(json.get('arrival_point')[0]),
                regular=regular,
            )
            if not regular:
                trip.date = today
                trip.interval_min = random.randint(0, 6)
                trip.interval_max = random.randint(0, 6)
            else:
                trip.dows = [dow for dow in range(0, 7) if random.random() < 0.5]
                if not trip.dows:
                    trip.dows = [1]
            if trip_type != Trip.OFFER:
                demand = TripDemand(
                    radius=random.choice(DEMAND_RADIUS_CHOICE)
                )
                demand.save()
                trip.demand = demand
            if trip_type != Trip.DEMAND:
                offer = TripOffer(
                    radius=random.choice(OFFER_RADIUS_CHOICE),
                    route=MultiLineString([GEOSGeometry(json.get('geometry')[0])])
                )
                offer.save()
                trip.offer = offer
            trip.save()
        except Exception, e:
            print "!!!!!!!!!!!!!!!!!!!!!", e
        #if index > 10:
        #    break
finally:
    route_file.close()

print "OK\n"
