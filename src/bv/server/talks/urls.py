# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *

urlpatterns = patterns('talks.views',
    (r'^mes_negociations/page/$', 'list_talk', {}, 'list_talks'),
    (r'^mes_negociations/page(?P<page>[0-9]+)/$', 'list_talk', {}, 'list_talks'),
    (r'^contacter_utilisateur/(?P<trip_id>\d+)/$', 'contact_user', {}, 'contact_user'),
    (r'^continuer_negociation/(?P<talk_id>\d+)/$', 'add_message', {}, 'add_message'),
    (r'^annuler_negociation/(?P<talk_id>\d+)/$', 'cancel_talk', {}, 'delete_talk'),
    (r'^supprimer_annonce_negociation/(?P<trip_id>\d+)/$', 'delete_trip', {}, 'delete_trip'),
    (r'^erreur_contact/$', 'error_contact', {}, 'error_contact'),
    (r'^valider_negociation/(?P<talk_id>\d+)/$', 'validate_talk', {}, 'validate_talk'),
    (r'^valider_negociation/confirmation/$', 'confirm_talk_validation',
        dict(
            template = 'talks/confirm_talk_validation.html',
            extra_context = {'current_item': 13}
        ), 'confirm_talk_validation'
    )
)
