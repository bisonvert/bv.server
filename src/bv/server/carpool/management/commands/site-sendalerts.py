# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import datetime
import os
import sys
     
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mail

from bv.server.carpool.models import Trip
from bv.server.utils.management import BaseCommand

class Command(BaseCommand):
    help = """Checks the match between announces if they have selected
    email alert option, and send mail with new alerts if there is some.
    
    An alert is thrown when there is a match betwen an offer and a demand
    """
        
    def __init__(self):
        BaseCommand.__init__(self)
        self.script_name = 'site-sendalerts'
        self.sent_mail = 0
        self.error_mail = 0
        self.no_mail = 0
    
    def handle(self, *args, **options): 
        mail_log = self.init_logger(options)
      
        mail_log.info_log("START")
        today = datetime.date.today()
        # trips created or modified yesterday - we fetch only ids
        last_trip_values = Trip.objects.filter(
            modification_date__lt=today,
            modification_date__gte=(today - datetime.timedelta(days=1))
        ).values('id')
        
        last_trip_values = Trip.objects.all().values('id')

        if last_trip_values:
            last_trip_ids = [value['id'] for value in last_trip_values]
            # trips with alert = True, not outdated
            for trip in Trip.objects.filter(alert=True).exclude_outdated():
                # check if mail exists
                if trip.user.email:
                    # send an email with the list of trips modified yesterday with are matching
                    self.send_mail(trip, self.get_matching_trips(trip, last_trip_ids), log=mail_log)
                else:
                    self.no_mail += 1
                    null_mail = '%s - Has no e-mail address' % (trip.user.username)
                    mail_log.info_log(null_mail)
                    
        mail_log.info_log(('%s mails sent' % (self.sent_mail)))
        mail_log.info_log(('%s empty mails' % (self.no_mail)))
        mail_log.info_log(('%s mails failure' % (self.error_mail)))
        mail_log.info_log("END")

    def get_matching_trips(self, trip, last_trip_ids):
        """
        Filter announces, and if there are matches, returns a list of these.
        """
        trips = []
        if trip.offer:
            # get demands, not outdated
            trip_demands = Trip.objects.get_demands(
                trip.offer.simple_route,
                trip.offer.direction_route,
                trip.offer.radius
            ).exclude(pk=trip.id).exclude_outdated()
            # date/dows params
            if trip.regular:
                trip_demands = trip_demands.filter_dows(trip.dows)
            else:
                trip_demands = trip_demands.filter_date_interval(
                    trip.date,
                    trip.interval_min,
                    trip.interval_max
                )
            # demands in the list of trips modified yesterday
            trip_demands = trip_demands.filter(id__in=last_trip_ids)
            # exclude user trips ?
            if settings.EXCLUDE_MY_TRIPS:
                trip_demands = trip_demands.exclude(user=trip.user)
            trips += trip_demands
        if trip.demand:
            # get offers, not outdated
            trip_offers = Trip.objects.get_offers(
                trip.departure_point,
                trip.arrival_point,
                trip.demand.radius
            ).exclude(pk=trip.id).exclude_outdated()
            # date/dows params
            if trip.regular:
                trip_offers = trip_offers.filter_dows(trip.dows)
            else:
                trip_offers = trip_offers.filter_date_interval(
                    trip.date,
                    trip.interval_min,
                    trip.interval_max
                )
            # offers in the list of trips modified yesterday
            trip_offers = trip_offers.filter(id__in=last_trip_ids)
            # exclude user trips ?
            if settings.EXCLUDE_MY_TRIPS:
                trip_offers = trip_offers.exclude(user=trip.user)
            # if demands retrieved, remove duplicated entries
            if trips:
                trip_offers = trip_offers.exclude(id__in=[trip.id for trip in trips])
            trips += trip_offers
        return trips

    def send_mail(self, trip, match_list, log):
        """Send an e-mail, containing announces list """
        if not match_list:
            return
        try:
            subject = u"Alertes BisonVert - annonce %s" % trip.name

            l = []
            for match in match_list:
                type = u"Offre" if match.trip_type == Trip.OFFER else (u"Demande" if match.trip_type == Trip.DEMAND else u"Indifférent")
                name = match.get_public_name()
                status = u"nouvelle annonce du" if match.creation_date.date() == match.modification_date.date() else u"annonce modifiée le"
                modif_time = match.modification_date.date().strftime("%d/%m/%Y")
                # FIXME the carpool reverse function
                # trip_url = self.get_absolute_url() # + match.get_absolute_url()
                l.append(u"* %s %s (%s %s)" % (type, name, status, modif_time))

            annonce_str = "\n".join(l)

            send_mail(
                subject,
                u"""Ceci est un message automatique, veuillez ne pas y répondre.

    Bonjour %(user)s,

    Voici la liste des annonces créés et/ou modifiées hier, correspondant à votre annonce %(trip)s:

    %(annonce)s

    Bon covoiturage avec %(annonce)s !""" % {
        'user'   : trip.user.username,
        'trip'   : trip.name,
        'annonce': annonce_str,
        'project': settings.PROJECT_NAME,
                },
            settings.FROM_EMAIL, [trip.user.email]
            )

# Nous vous rappelons que vous pouvez consultez à tout moment la liste des annonces
# qui correspondent à votre annonce %s à l'adresse suivante:
# %s%s
# trip.name,
# self.get_absolute_url(),
# FIXME the carpool reverse function
# reverse('carpool:show_trip_results', args=[trip.id]),

            self.sent_mail += 1
        except:
            self.error_mail += 1
            log.error_log(sys.exc_info())
