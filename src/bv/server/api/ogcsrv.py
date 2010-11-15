# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from mapnik2 import Style, Rule, Color, Layer, PostGIS
from mapnik2 import PointSymbolizer, LineSymbolizer

from ogcserver.configparser import SafeConfigParser
from ogcserver.exceptions import ServerConfigurationError, OGCException
from ogcserver.WMS import BaseWMSFactory

from bv.server.carpool.models import Trip

class WMSFactory(BaseWMSFactory):
    def __init__(self):
        BaseWMSFactory.__init__(self)
        #self.loadXML(settings.MAPNIK_XMLFILE)

class WMSHandler(object):
    """WMS Handler."""
    def __init__(self):
        conf = SafeConfigParser()
        conf.readfp(open(settings.MAPNIK_CONFIGFILE))
        self.conf = conf
        self.mapfactory = WMSFactory()

    def process_trip(self, request, reqparams):
        """Process Trip request."""
        if not 'trip_id' in reqparams:
            return

        trip_id = reqparams['trip_id']
        trip = get_object_or_404(Trip, pk=trip_id, offer__id__isnull=False)

        new_style_name = "trip_style"
        if new_style_name not in self.mapfactory.styles:
            new_style = Style()
            new_rule = Rule()
            new_rule.symbols.append(PointSymbolizer())
            new_rule.symbols.append(LineSymbolizer(
                Color('#2a4776'), 2)
            )
            new_style.rules.append(new_rule)
            self.mapfactory.register_style(new_style_name, new_style)

        styles = {new_style_name: new_style_name}

        new_layer_name = "trip_%s" % trip_id
        str_new_layer_name = "%s_aggragatestyle" % new_layer_name

        if new_layer_name not in self.mapfactory.layers:
            new_layer = Layer(new_layer_name)
            new_layer.queryable = True
            new_layer.datasource = PostGIS(
                host=settings.DATABASE_HOST,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                port=settings.DATABASE_PORT,
                dbname=settings.DATABASE_NAME,
                table="(SELECT route FROM carpool_tripoffer o LEFT JOIN carpool_trip t ON t.offer_id=o.id WHERE t.id=%s) geom" % trip.offer_id
            )
            new_layer.srs = '+init=epsg:4326'
            new_layer.styles.append(str_new_layer_name)

            self.mapfactory.register_aggregate_style(str_new_layer_name, styles)
            self.mapfactory.register_layer(new_layer, str_new_layer_name)

    def process(self, request):
        """Process request."""
        reqparams = {}
        for key, value in request.GET.items():
            reqparams[key.lower()] = str(value)

        # create dynamic styles and layers
        self.process_trip(request, reqparams)
        self.mapfactory.finalize()

        # process request
        onlineresource = 'http://%s:%s%s?' % (request.META['SERVER_NAME'],
                request.META['SERVER_PORT'], request.META['SCRIPT_NAME'])
        if not reqparams.has_key('request'):
            raise OGCException('Missing request parameter.')
        request = reqparams['request']
        del reqparams['request']
        if request == 'GetCapabilities' and not reqparams.has_key('service'):
            raise OGCException('Missing service parameter.')
        if request in ['GetMap', 'GetFeatureInfo']:
            service = 'WMS'
        else:
            service = reqparams['service']
        if reqparams.has_key('service'):
            del reqparams['service']
        try:
            try:
                mapnikmodule = __import__('ogcserver.' + service)
            except Exception, e:
                print "service: %s could not be imported" % service
        except:
            raise OGCException('Unsupported service "%s".' % service)
        servicehandlerfactory = getattr(mapnikmodule, service).ServiceHandlerFactory
        servicehandler = servicehandlerfactory(self.conf, self.mapfactory,
                onlineresource, reqparams.get('version', None))
        if reqparams.has_key('version'):
            del reqparams['version']
        if request not in servicehandler.SERVICE_PARAMS.keys():
            raise OGCException('Operation "%s" not supported.' % request,
                    'OperationNotSupported')
        ogcparams = servicehandler.processParameters(request, reqparams)
        try:
            requesthandler = getattr(servicehandler, request)
        except:
            raise OGCException('Operation "%s" not supported.' % request,
                    'OperationNotSupported')

        resp = requesthandler(ogcparams)
        data = resp.content
        response = HttpResponse(data, content_type=resp.content_type)
        return response
