"""A set of tools to compute and work with SIG related operations

"""
# python import 
import simplejson

# django imports
from django.contrib.gis.geos import GEOSGeometry, LineString, MultiLineString
from django.http import HttpResponse, Http404

# bv imports
from utils.geodjango import smart_transform
from bv.server.carpool import MAX_DISTANCE_DRIVER, MAX_DISTANCE_PASSENGER, MAX_INTERVAL, \
    SRID_DEFAULT, SRID_TRANSFORM, str_slugify
from api.ogcserver import WMSHandler

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

def ogcserver(request):
    """OGCServer main view."""
    wmshandler = WMSHandler()
    response = wmshandler.process(request)
    return response
