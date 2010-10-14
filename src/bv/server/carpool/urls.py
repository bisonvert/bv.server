# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.conf.urls.defaults import *
from bv.server.carpool.models import Trip
from django.conf import settings

urlpatterns = patterns('carpool.views',
    (r'^$', 'home', {}, 'home'),
    (r'^mes_annonces/$', 'my_trips', {}, 'list_user_trips'),
    (r'^mes_annonces/page(?P<page>[0-9]+)/$', 'my_trips', {}, 'list_user_trips'),
    (r'^sauver_recherche/$', 'add_trip_from_search', {}, 'save_search'),
    (r'^nouvelle_annonce/$', 'add_modify_trip', {}, 'add_trip'),
    (r'^modifier_annonce/(?P<trip_id>\d+)/$', 'add_modify_trip', {}, 'edit_trip'),
    (r'^annonce_retour/(?P<trip_id>\d+)/$', 'add_return_trip', {}, 'add_return_trip'),
    (r'^resultats_annonce/(?P<trip_id>\d+)/$', 'trip_results', {}, 'show_trip_results'),
    (r'^supprimer_annonce/(?P<trip_id>\d+)/$', 'delete_trip', {}, 'delete_trip'),
    (r'^annonces_covoiturage/page(?P<page>[0-9]+)/$', 'trip_list', {}, 'list_trips'),

    #"Ajax" urls
    (r'^ajax/get_trips/(?P<trip_id>\d+)/$', 'get_trip_results', {}, 'ajax_get_trip_results'),
    (r'^ajax/switch_alert/(?P<trip_id>\d+)/$', 'switch_alert', {}, 'ajax_edit_alert'),
    (r'^ajax/get_trips/$', 'get_trips', {}, 'ajax_get_trips'),
    
    # Search for a trip
    (r'^chercher_offre_covoiturage/$', 'search_trip', {'trip_type': Trip.OFFER}, 'search_offer_trip'),
    (r'^chercher_demande_covoiturage/$', 'search_trip', {'trip_type': Trip.DEMAND}, 'search_demand_trip'),
    (r'^chercher_offre_covoiturage/(?P<departure_slug>[-\w]+)-(?P<departure_zip>\d{2})_(?P<arrival_slug>[-\w]+)-(?P<arrival_zip>\d{2})/$', 'robots_search_trip', {'trip_type': Trip.OFFER}, 'robots_search_offer_trip'),
    (r'^chercher_demande_covoiturage/(?P<departure_slug>[-\w]+)-(?P<departure_zip>\d{2})_(?P<arrival_slug>[-\w]+)-(?P<arrival_zip>\d{2})/$', 'robots_search_trip', {'trip_type': Trip.DEMAND}, 'robots_search_demand_trip'),

    # Departure from, Arrival to
    (r'^au_depart_de/a_destination_de/$', 'choose_depart_from_arrival_to', {}, 'choose_departure_from_arrival_to'),
    (r'^au_depart_de/(?P<departure_slug>[-\w]+)-(?P<departure_zip>\d{2})/page(?P<page>[0-9]+)/$', 'depart_from', {}, 'show_departure_from'),
    (r'^a_destination_de/(?P<arrival_slug>[-\w]+)-(?P<arrival_zip>\d{2})/page(?P<page>[0-9]+)/$', 'arrival_to', {}, 'show_arrival_to'),

    # Public profile
    (r'^annonce_covoiturage/(\d{2}-\d{2}-\d{4})_([-\w]+)_([-\w]+)_(?P<trip_id>\d+)/$', 'trip_details', {}, 'ajax_get_trip_details_punctual'),
    (r'^annonce_covoiturage/([-\w]*)_([-\w]+)_([-\w]+)_(?P<trip_id>\d+)/$', 'trip_details', {}, 'ajax_get_trip_details_regular'),

)
