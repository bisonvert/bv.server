# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^contact/$', 'bv.server.pages.views.contact', {}, 'contact_us'),
    (r'^contact/message_ok/$', 'django.views.generic.simple.direct_to_template',
        {
        'template': 'carpool/confirm_contact.html',
        'extra_context': {'current_footer_item': 2}
        }, 'confirm_contact'),
)
