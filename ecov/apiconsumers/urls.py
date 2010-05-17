from django.conf.urls.defaults import *

urlpatterns = patterns('apiconsumers.views',
    url(r'^create/$', 'create_consumer', {}, 'create'),
    url(r'^$', 'list_consumers', {}, 'list'),
    url(r'^pending/$', 'list_pending_consumers', {}, 'pending'),
    url(r'^validate/(?P<consumer_id>\d+)/$', 'validate_consumer', {}, 'validate'),
    url(r'^validate/all/$', 'validate_all_pending_consumers', {}, 'validate_all'),
)
