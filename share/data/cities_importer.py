# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from bv.server.carpool.models import City
from bv.server.carpool import str_slugify, SRID_DEFAULT

from django.contrib.gis.geos import GEOSGeometry
from django.utils.encoding import smart_unicode

import re

INPUT_PATH = '/home/zebuline/projets/covoiturage/share/data/'
INPUT_FILE = 'cities_fr.csv'

DATA = {
    'NAME': 0,
    'UPNAME': 1,
    'ZIPCODE': 2,
    'INSEECODE': 3,
    'COUNTRYCODE': 4,
    'LAT': 5,
    'LNG': 6,
}

input_file = open("%s%s" % (INPUT_PATH, INPUT_FILE), mode= 'r')

try:
    for line in input_file:
        try:
            if re.search('^#', line):
                # next
                continue

            data = [ d.strip() for d in line.split(';') ]
            #print data

            lat = data[DATA['LAT']] if data[DATA['LAT']] != '-' else "0"
            lng = data[DATA['LNG']] if data[DATA['LNG']] != '-' else "0"
            lat = re.sub(',', '.', lat)
            lng = re.sub(',', '.', lng)

            name = smart_unicode(data[DATA['NAME']])
            city = City(
                name = name,
                slug = str_slugify(name),
                zipcode = int(data[DATA['ZIPCODE']]),
                point = GEOSGeometry('POINT( %s %s )' % (lng, lat), srid=SRID_DEFAULT),
                insee_code = int(data[DATA['INSEECODE']]),
                population = 0
            )
            print city, city.slug
            city.save()
        except Exception, e:
            print "!!!!!!!!!!!!!!!!!!!!!", line, e
finally:
    input_file.close()

print "OK\n"
