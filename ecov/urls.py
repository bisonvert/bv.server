# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from feeds import RSSFeed, AtomFeed
admin.autodiscover()

# Custom handler 500
handler500 = 'pages.views.server_error'
js_info_dict = {'packages': ('carpool'),}

urlpatterns = patterns('',
    #Include app urls
    (r'^', include('carpool.urls', namespace='carpool')),
    (r'^', include('pages.urls', namespace='pages')),
    (r'^utilisateurs/', include('accounts.urls', namespace='accounts')),
    (r'^mes_evaluations/', include('rating.urls', namespace='rating')),
    (r'^discussions/', include('talks.urls', namespace='talks')),
    (r'^admin/(.*)', admin.site.root),
    (r'^ogcserver/$', 'ogcserver.views.ogcserver'),

    #Ajax
    (r'^ajax/calculate_buffer/$', 'carpool.misc.calculate_buffer'),
    (r'^ajax/get_city/$', 'carpool.misc.get_city'),
    (r'^ajax/reverse_geocode/$', 'utils.reverse_geocoding.reverse_geocoder'),

    #Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': { 'rss': RSSFeed, 'atom': AtomFeed }}),

    #I18n
    (r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    
    #API
    (r'^api/', include('api.urls', namespace='api')),
     
)

#OAUTH
urlpatterns += patterns('piston.authentication',
    url(r'^oauth/request_token/$', 'oauth_request_token', name='oauth_request_token'),
    url(r'^oauth/access_token/$', 'oauth_access_token', name='oauth_access_token'),
    url(r'^oauth/authorize/$', 'oauth_user_auth', name='oauth_user_auth'),
)   

if settings.DEBUG:
    urlpatterns += patterns('',
        # create routes
        (r'^set_language/$', 'direct_to_template', {
            'template': 'carpool/set_language.html'
        }),
        # Media
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
