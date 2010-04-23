# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
    (r'^login/$', 'login', {'template_name':'accounts/login.html'}, 'login'),
    (r'^nouveau_mdp/$', 'new_password', {}, 'new_password'),
    (r'^inscription/$', 'register', {}, 'register'),
    (r'^validation_email/(?P<key>\w{50})/$', 'validate_email', {}, 'validate_email'),
    (r'^mon_compte/$', 'my_account', {}, 'show_user_account'),
    (r'^mon_compte/mon_profil/$', 'edit_profile', {}, 'edit_user_profile'),
    (r'^mon_compte/mes_preferences/$', 'edit_preferences', {}, 'edit_user_preferences'),
    (r'^mes_contacts/$', 'edit_contact', {}, 'edit_user_contacts'),
)

urlpatterns += patterns('',
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login', {}, 'logout'),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^confirmation_nouveau_mdp/$', 'direct_to_template', {
        'template': 'accounts/confirm_new_password.html',
        'extra_context': {'current_item': 2}
    }, 'confirm_new_password'),
    (r'^confirmation_inscription/$', 'direct_to_template', {
        'template': 'accounts/confirm_registration.html',
        'extra_context': {'current_item': 2}
    }, 'confirm_registration'),
    (r'^robots.txt$', 'direct_to_template', {
        'template': 'robots.html',
        'mimetype': 'text/plain',
    }),
)
