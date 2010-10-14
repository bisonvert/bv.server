# -*- coding: utf-8 -*-

from django.conf import settings
from bv.server.carpool.models import City
import re

"""Context processors

Add variables to context for RequestContect responses  and generic views

A Context Processor must be added into settings
::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'myapp.mycontextprocessors.mycontextprocessor',
    )
    
Here's how to use the context processors
::

    from django.template import RequestContext
    from django.shortcuts import render_to_response

    return render_to_response('path/to/template.html', {
        'foo': bar, 
        'blah': toto
    }, context_instance=RequestContext(request))

"""

_BIG_CITIES = City.objects.all().order_by('-population')[:14]
_R_SPECIFIC_HOME = re.compile(r'^/(\w+)/$')
_CACHE_FOOTER_CITIES_FROM = {}
_CACHE_FOOTER_CITIES_TO = {}

def admin_media_url(request):
    """ADMIN_MEDIA_URL: URL d'accès aux media admin."""
    return {
        'ADMIN_MEDIA_URL': settings.ADMIN_MEDIA_PREFIX
    }

def js_ext(request):
    """JS_EXT: Extension des fichiers javascript: .js ou -min.js en fonction
    du paramétrage.

    """
    return {
        'JS_EXT': settings.JS_EXT
    }

def project_info(request):
    """Informations sur le projet.

    + PROJECT_NAME: Nom du projet (BisonVert).
    + PROJECT_NAME_URL: Nom du projet + extension (BisonVert.net).
    + PROJECT_ROOT_URL: URL racine du projet.

    """
    return {
        'PROJECT_NAME': settings.PROJECT_NAME,
        'PROJECT_NAME_URL': settings.PROJECT_NAME_URL,
        'PROJECT_ROOT_URL': request.build_absolute_uri('/').strip('/')
    }

def get_footer_cities(request):
    """En fonction du paramétrage, récupère les villes affichées dans le footer
    Au départ de et/ou à destination de

    + FOOTER_CITIES: contient ces villes
    """
    match_path_info = _R_SPECIFIC_HOME.match(request.META['PATH_INFO'])
    if match_path_info and match_path_info.group(1) in settings.HOME_PAGES_AVAILABLE:
        # specific home page
        theme_used = match_path_info.group(1)
    else:
        theme_used = settings.THEME_USED

    footer_cities = {}

    if settings.HOME_PAGES[theme_used]['from'] is None:
        # Bigest
        footer_cities.update({'FROM': _BIG_CITIES})
    elif settings.HOME_PAGES[theme_used]['from'] is False:
        # No from
        footer_cities.update({'FROM': []})
    else:
        # get cities from settings
        if theme_used not in _CACHE_FOOTER_CITIES_FROM:
            _CACHE_FOOTER_CITIES_FROM[theme_used] = City.objects.filter(pk__in=settings.HOME_PAGES[theme_used]['from'])
        footer_cities.update({
            'FROM': _CACHE_FOOTER_CITIES_FROM[theme_used]
        })

    if settings.HOME_PAGES[theme_used]['to'] is None:
        # Bigest
        footer_cities.update({'TO': _BIG_CITIES})
    elif settings.HOME_PAGES[theme_used]['to'] is False:
        # No to
        footer_cities.update({'TO': []})
    else:
        # get cities from settings
        if theme_used not in _CACHE_FOOTER_CITIES_TO:
            _CACHE_FOOTER_CITIES_TO[theme_used] = City.objects.filter(pk__in=settings.HOME_PAGES[theme_used]['to'])
        footer_cities.update({
            'TO': _CACHE_FOOTER_CITIES_TO[theme_used]
        })

    return {'FOOTER_CITIES': footer_cities}

def get_google_analytics_info(request):
    """Informations Google Analytics.

    + GOOGLE_ANALYTICS_ENABLE: Google Analytics activé ou non.
    + GOOGLE_ANALYTICS_KEY: Clé du compte Google Analytics.

    """
    return {
        'GOOGLE_ANALYTICS_ENABLE': settings.GOOGLE_ANALYTICS_ENABLE,
        'GOOGLE_ANALYTICS_KEY': settings.GOOGLE_ANALYTICS_KEY,
    }

def get_google_adsense_info(request):
    """Informations Google AdSense.

    + GOOGLE_ADSENSE_ENABLE: Google AdSense activé ou non.
    + GOOGLE_ADSENSE_KEY: clé du compte Google AdSense.
    + GOOGLE_ADSENSE_SLOT: Slot de la pub générée sur le site de Google
      AdSense.
    + GOOGLE_ADSENSE_WIDTH: largeur de la pub générée sur le site de Google
      AdSense.
    + GOOGLE_ADSENSE_HEIGHT: hauteur de la pub générée sur le site de Google
      AdSense.

    """
    return {
        'GOOGLE_ADSENSE_ENABLE': settings.GOOGLE_ADSENSE_ENABLE,
        'GOOGLE_ADSENSE_KEY': settings.GOOGLE_ADSENSE_KEY,
        'GOOGLE_ADSENSE_SLOT': settings.GOOGLE_ADSENSE_SLOT,
        'GOOGLE_ADSENSE_WIDTH': settings.GOOGLE_ADSENSE_WIDTH,
        'GOOGLE_ADSENSE_HEIGHT': settings.GOOGLE_ADSENSE_HEIGHT,
    }

def with_title_header(request):
    """Avec ou sans titre BV dans le header."""
    match_path_info = _R_SPECIFIC_HOME.match(request.META['PATH_INFO'])
    if match_path_info and match_path_info.group(1) in settings.HOME_PAGES_AVAILABLE:
        # specific home page
        theme_used = match_path_info.group(1)
    else:
        theme_used = settings.THEME_USED
    return {'WITH_TITLE_HEADER': settings.HOME_PAGES[theme_used]['title_header']}

def with_tools(request):
    """Avec ou sans outils: avec un bv skinné, pas d'outils."""
    return {'WITH_TOOLS': settings.THEME_USED == 'default'}

def client_urls(request):
    """Provides a dict to the templates, with the urls of the client actions."""
   
    dict = {} 
    for category, urls in settings.DEFAULT_CLIENT_URLS.items():
        if category != 'root':
            dict[category] = {}
            for name, url in urls.items():
                if url.count("%s") == 1:
                    dict[category][name] = url % settings.DEFAULT_CLIENT_ROOT_URL
    
    return {'client_urls' : dict}
