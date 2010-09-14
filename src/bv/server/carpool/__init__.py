# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.contrib.gis.geos import LineString, MultiLineString, GEOSGeometry
from utils.geodjango import smart_transform

import re
import unicodedata

MAX_DISTANCE_DRIVER = 20000
MAX_DISTANCE_PASSENGER = 20000
MAX_INTERVAL = 7
SRID_DEFAULT = 4326
SRID_TRANSFORM = 27572

MAX_NUM_POINTS = 100
TOLERANCE = 50
MIN_TOLERANCE = 10

R_CITY_ZIP = re.compile(r'^([\w-]+)-(\d{2})$')

def str_slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def get_simple_route(route):
    """Retourne une version simplifiée d'une route."""
    num_points = route.num_points
    if num_points <= MAX_NUM_POINTS:
        return route
    tolerance = TOLERANCE
    if num_points <= MAX_NUM_POINTS*3:
        tolerance = MIN_TOLERANCE
    route = smart_transform(route,SRID_TRANSFORM, from_srid=SRID_DEFAULT)
    simple_route = route.simplify(tolerance)
    ogr = simple_route.ogr
    ogr.transform(SRID_DEFAULT)
    return GEOSGeometry(ogr.wkb, SRID_DEFAULT)

def get_direction_route(route):
    if isinstance(route, LineString):
        multilinestring = MultiLineString([route])
    else:
        multilinestring = route
    num_points = route.num_points
    mod = num_points / MAX_NUM_POINTS or 1
    index = 0
    points = []
    for linestring in multilinestring:
        for point in linestring:
            index += 1
            if not index % mod or index == 0 or index == num_points-1:
                points.append(point)
    return LineString(points)
