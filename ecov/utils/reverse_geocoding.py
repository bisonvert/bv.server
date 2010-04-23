# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Reverse Geocoding Tool - Idea from http://geopy.googlecode.com/"""

from django.http import HttpResponse
from django.utils import simplejson

import sys
import xml.dom.minidom
from urllib import urlencode
from urllib2 import urlopen
from xml.parsers.expat import ExpatError

import re

R_DISTRICT = re.compile(r' ?\d+')

def reverse_geocoder(request):
    """Vue généralement appelée en AJAX. Retourne du JSON.
    Paramètres: lat, lng - Coordonnées du point à reverse-géocoder.
    Retourne le reverse-geocodage des paramètres, sous la forme 'Ville
    (numéro du département)'.

    Ne fonctionne que sur les données françaises.

    """
    lat = float(request.REQUEST['lat'])
    lng = float(request.REQUEST['lng'])

    rgeocoder = ReverseGeocoder()
    (city_name, city_zip, country_code) = rgeocoder.reverse({
        'lat': lat,
        'lng': lng,
        'maxRows': 1,
    })
    response_dict = {}
    if city_name and city_zip and country_code == 'FR':
        response_dict = {
            'city_name': u"%s (%s)" % (city_name, int(city_zip)/1000)
        }

    resp = HttpResponse()
    simplejson.dump(
        response_dict,
        resp,
        ensure_ascii=False,
        separators=(',',':')
    )
    return resp

class WebReverseGeocoder(object):
    """A ReverseGeocoder subclass with utility methods helpful for handling
    results given by web-based reverse-geocoders.

    """

    @classmethod
    def _get_encoding(cls, page, contents=None):
        """Get the last encoding (charset) listed in the header of ``page``."""
        plist = page.headers.getplist()
        if plist:
            key, value = plist[-1].split('=')
            if key.lower() == 'charset':
                return value
        if contents:
            try:
                return xml.dom.minidom.parseString(contents).encoding
            except ExpatError:
                pass

    @classmethod
    def _decode_page(cls, page):
        """Read the encoding (charset) of ``page`` and try to encode it using
        UTF-8.

        """
        contents = page.read()
        encoding = cls._get_encoding(page, contents) or sys.getdefaultencoding()
        return unicode(contents, encoding=encoding).encode('utf-8')

    @classmethod
    def _get_first_text(cls, node, tag_names, strip=None):
        """Get the text value of the first child of ``node`` with tag
        ``tag_name``. The text is stripped using the value of ``strip``.

        """
        if isinstance(tag_names, basestring):
            tag_names = [tag_names]
        if node:
            while tag_names:
                nodes = node.getElementsByTagName(tag_names.pop(0))
                if nodes:
                    child = nodes[0].firstChild
                    return child and child.nodeValue.strip(strip)

    @classmethod
    def _join_filter(cls, sep, seq, pred=bool):
        """Join items in ``seq`` with string ``sep`` if pred(item) is True.
        Sequence items are passed to unicode() before joining.

        """
        return sep.join([unicode(i) for i in seq if pred(i)])

class ReverseGeocoder(WebReverseGeocoder):
    """A ReverseGeocoder based on Geonames API."""
    def __init__(self, output_format='json'):
        self.output_format = output_format

    @property
    def url(self):
        """Build the Geonames URL with GET arguments"""
        domain = "ws.geonames.org"
        output_format = self.output_format.lower()
        append_formats = {'json': 'JSON'}
        resource = ("findNearbyPostalCodes" +
                append_formats.get(output_format, ''))
        return "http://%(domain)s/%(resource)s?%%s" % locals()

    def reverse(self, params):
        """Performs the reverse geocoding"""
        url = self.url % urlencode(params, True)
        return self.reverse_url(url)

    def reverse_url(self, url):
        """Get the Geonames URL and dispatch the result"""
        page = urlopen(url)
        dispatch = getattr(self, 'parse_' + self.output_format)
        return dispatch(page)

    def parse_json(self, page):
        """Parses the json response of reverse geocoding"""
        if not isinstance(page, basestring):
            page = self._decode_page(page)
        json = simplejson.loads(page)
        codes = json.get('postalCodes', [])

        def parse_code(code):
            """Parse a code"""
            place_name = code.get('placeName')
            place_name = R_DISTRICT.sub('', place_name)
            postal_code = code.get('postalCode')
            country_code = code.get('countryCode')
            return (place_name, postal_code, country_code)

        return parse_code(codes[0]) if codes else (None, None, None)
