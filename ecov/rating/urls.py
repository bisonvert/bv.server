# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *

urlpatterns = patterns('rating.views',
    (r'^mes_evaluations/$', 'my_reports', {}, 'show_user_reports'),
    (r'^mes_evaluations/evaluations_recues/$', 'list_my_reports', {}, 'list_user_reports'),
    (r'^mes_evaluations/evaluations_recues/page(?P<page>[0-9]+)/$', 'list_my_reports', {}, 'list_user_reports'),
    (r'^mes_evaluations/evaluations_donnees/page(?P<page>[0-9]+)/$', 'list_other_reports', {}, 'list_other_reports'),
    (r'^mes_evaluations/evaluations_encours/page(?P<page>[0-9]+)/$', 'list_tempreports', {}, 'list_temp_reports'),
    (r'^mes_evaluations/evaluations_encours/evaluer/(?P<tempreport_id>\d+)/$', 'rate_user', {}, 'rate_user'),
)
