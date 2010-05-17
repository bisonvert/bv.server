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
    # API URLs
    (r'^', include('api.urls', namespace='api')),
    (r'^consumers/', include('apiconsumers.urls', namespace='apiconsumers')),

    #Include app urls
    (r'^', include('pages.urls', namespace='pages')),
    (r'^account/', include('accounts.urls', namespace='accounts')),
    (r'^admin/(.*)', admin.site.root),

    #Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': { 'rss': RSSFeed, 'atom': AtomFeed }}),

    #I18n
    (r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
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
