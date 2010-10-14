# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import datetime
from optparse import make_option
import os
import sys

from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from bv.server.utils.management import BaseCommand
from rating.models import TempReport

class Command(BaseCommand):
    script_name = 'send-rating-alerts'
    help = """Get temp evaluations for wich a mail hasn't be sent yet to both persons 
    of the Carpooling trip. 

    For each temporary evaluation, send a mail with a link to the evaluation 
    form."""
    
    def __init__(self):
        super(Command, self).__init__()
        self.script_name = 'send-rating-alerts'
        
    def handle(self, *args, **options):    
        run_logger = self.init_logger(options)
        run_logger.info_log("START run_alert")
        
        nb_reports_ok = 0
        nb_reports_error = 0
        nb_mail_sent = 0
        
        # get all temp evaluation to proceed
        tempreports = TempReport.objects.get_opened_tempreports().filter(
                mail_sent=False)
        
        for report in tempreports:
            try:
                _send_mail(report.user1, report.user2, report.id)
                nb_mail_sent += 1
                _send_mail(report.user2, report.user1, report.id)
                nb_mail_sent += 1
                report.mail_sent = True
                report.save()
                nb_reports_ok += 1
            except Exception, err:
                nb_reports_error += 1
                run_logger.error_log(sys.exc_info())

        run_logger.info_log("%d emails sent" % nb_mail_sent)
        run_logger.info_log("%d temp reports successfully treated" % nb_reports_ok)
        run_logger.info_log("%d temp reports in error" % nb_reports_error)
        run_logger.info_log("END run_alert")
        
    def _send_mail(self, user1, user2, tempreport_id):
        """
        Send a mail to user1, to prevent that he can evaluate user2, providing
        a link to the evaluation form
        """
        send_mail(
            u"Evaluez votre partenaire de covoiturage !",
            u"""Ceci est un message automatique, veuillez ne pas y répondre.

Bonjour %s,

Vous avez négocié un trajet avec %s. Ce trajet doit à ce jour avoir été
effectué.

Vous pouvez dès à présent évaluer votre partenaire de covoiturage, en
remplissant le formulaire à l'adresse suivante:
%s%s

Cordialement,
L'équipe %s""" % (
                user1.username,
                user2.username,
                self.get_absolute_url(),
                reverse('rate_user', args=[tempreport_id]),
                settings.PROJECT_NAME
            ),
            settings.FROM_EMAIL, [user1.email]
        )

