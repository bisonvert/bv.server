# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *

urlpatterns = patterns('bv.server.accounts.views',
    (r'^$', 'my_account', {}, 'show_user_account'),
    (r'^login/$', 'login', {'template_name':'accounts/login.html'}, 'login'),
    (r'^change_password/$', 'new_password', {}, 'new_password'),
    (r'^register/$', 'register', {}, 'register'),
    (r'^register/confirm_mail/(?P<key>\w{50})/$', 'validate_email', {}, 'validate_email'),
    (r'^profile/$', 'edit_profile', {}, 'edit_user_profile'),
    (r'^preferences/$', 'edit_preferences', {}, 'edit_user_preferences'),
    (r'^contacts/$', 'edit_contact', {}, 'edit_user_contacts'),
)

urlpatterns += patterns('',
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login', {}, 'logout'),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^change_password/confirm/$', 'direct_to_template', {
        'template': 'accounts/confirm_new_password.html',
        'extra_context': {'apiconsumers': True}
    }, 'confirm_new_password'),
    (r'^register/confirm/$', 'direct_to_template', {
        'template': 'accounts/confirm_registration.html',
        'extra_context': {'apiconsumers': True}
    }, 'confirm_registration'),
    (r'^robots.txt$', 'direct_to_template', {
        'template': 'robots.html',
        'mimetype': 'text/plain',
    }),
)
