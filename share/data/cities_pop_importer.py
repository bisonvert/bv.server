# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from bv.server.carpool.models import City
from bv.server.carpool import str_slugify, SRID_DEFAULT

from django.contrib.gis.geos import GEOSGeometry
from django.utils.encoding import smart_unicode

import re

INPUT_PATH = '/home/zebuline/projets/covoiturage/share/data/'
INPUT_FILE = 'cities_pop_fr.csv'

DATA = {
    'DP': 0,
    'INSEECODE': 1,
    'NAME': 2,
    'PFX': 3,
    'POPULATION': 4,
    'DENSITY': 5,
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

            try:
                city = City.objects.get(insee_code=data[DATA['INSEECODE']])
            except City.DoesNotExist, e:
                print line
                continue
            city.population = int(data[DATA['POPULATION']])

            #print city, city.population
            city.save()
        except Exception, e:
            print "!!!!!!!!!!!!!!!!!!!!!", line, e
finally:
    input_file.close()

print "OK\n"
