# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
"""Provides a common way to interact with bisonvert serverside talks data 

"""
# django imports
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

# ecov imports
from carpool.models import Trip
from rating.models import TempReport
from talks.models import Talk, Message
from talks.forms import ContactUserForm

# lib imports
from lib.exceptions import *

class LibTalks:
    def _get_ordering(self):
        return {
            'departure': ['carpool_trip.departure_city'],
            '-departure': ['-carpool_trip.departure_city'],
            'arrival': ['carpool_trip.arrival_city'],
            '-arrival': ['-carpool_trip.arrival_city'],
            'date': ['carpool_trip.dows', 'carpool_trip.date'],
            '-date': ['-carpool_trip.dows', '-carpool_trip.date'],
            'time': ['carpool_trip.time'],
            '-time': ['-carpool_trip.time'],
            'type': ['type'],
            '-type': ['-type'],
            'contact': ['auth_user.username'],
            '-contact': ['-auth_user.username'],
        }
        
    def list_talks(self, user, ordered_by=None):
        """List of talks (negotiations) for the given user.
        
        """
        ordered_by = ordered_by or 'date'
        oargs = self._get_ordering()[ordered_by]
        return Talk.objects.select_related().filter(
            Q(from_user=user) | Q(trip__user=user)).extra(
                    select={
                        'type': 'CASE WHEN carpool_trip.demand_id IS NULL THEN 0 '
                        'WHEN carpool_trip.offer_id IS NULL THEN 1 ELSE 2 END'
                    }
                ).order_by(*oargs)

    def list_messages(self, user, talk_id):
        """Return the list of messages for a given talk.
        
        - If the user is not valid, raise a InvalidUser Exception
        - if the talk does not exists, raise a TalkDoesNotExist exception
        
        """
        try:
            talk = Talk.objects.get(id=talk_id)
        except Talk.DoesNotExist:
            raise TalkDoesNotExist(talk_id)
        
        if (talk.from_user.id != user.id and talk.trip.user.id != user.id):
            raise InvalidUser(user)
            
        return talk.message_set.all()
        
    @transaction.commit_manually
    def contact_user(self, user, trip_id, post_data):
        """Create a new negociation about an announce
        
        Create the negotiation, the message, and send a mail to the user trip.
        
        If the trip doesnt exists, raise a TripDoesNotExist exception.
        If a negociation already exists for this announce and this user, raise 
        an TalkAlreadyExist exception.
        
        If one of the email field is empty, raise a InvalidMail exception.

        """
        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            raise TripDoesNotExist(trip_id)
        try:
            talk = Talk.objects.get(trip=trip, from_user=user)
            raise TalkAlreadyExists(trip_id)
        except Talk.DoesNotExist:
            pass

        if user.email == "" or trip.user.email == "":
            raise InvalidMail()

        from_user = user
        to_user = trip.user
        subject = _("Trip %(trip_public_name)s") % {
            'trip_public_name': trip.get_public_name()
        }
       
        form = ContactUserForm(post_data)
        if not form.is_valid():
            raise InvalidContactUserForm(form)
        try:
            talk = Talk(
                trip=trip,
                from_user=from_user
            )
            talk.save()
            self._send_message(
                talk,
                from_user,
                to_user,
                form.cleaned_data['message']
            )
        except Exception, err:
            transaction.rollback()
            raise err
        else:
            transaction.commit()
            return talk
            
    @transaction.commit_manually
    def add_message(self, user, talk_id, post_data):
        """Add a message to an already existing negociation talk, and send a 
        mail to the user.
        
        - If the talk doesnt exists, raise a TalkDoesNotExist exception
        - If the provided post_data is not valid, raise a InvalidContactUserForm
        - If the user is not allowed to retreive this data, raise a InvalidUser
          exception.

        """
        try:
            talk = Talk.objects.get(id=talk_id, from_user=user)
        except Talk.DoesNotExist:
            raise TalkDoesNotExist(trip_id)
            
        if (talk.from_user.id != user.id and talk.trip.user.id != user.id):
            raise InvalidUser(user)

        from_user = user
        to_user = (talk.trip.user if from_user.id == talk.from_user.id
                else talk.from_user)
                
        subject = _("Trip %(trip_public_name)s") % {
            'trip_public_name': talk.trip.get_public_name()
        }
        
        form = ContactUserForm(post_data)
        if form.is_valid():
            try:
                self._send_message(
                    talk,
                    from_user,
                    to_user,
                    form.cleaned_data['message']
                )
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()
                return talk
       
    @transaction.commit_manually
    def cancel_talk(self, user, talk_id, post_data):
        """Cancel the negotiation talk
        
        Delete the negociation talk and associated messages, send a mail to 
        the other user.
        
        Canceling a negociation talk must have a reason. So, we use the contact 
        form.
        
        - If the talk doesnt exists, raise a TalkDoesNotExist exception
        
        """
        try:
            talk = Talk.objects.get(pk=talk_id)
        except Talk.DoesNotExist:
            raise TalkDoesNotExist(talk_id)
            
        if (talk.from_user.id != user.id and talk.trip.user.id != user.id):
            raise InvalidUser(user)

        form = ContactUserForm(post_data)
        
        if not form.is_valid():
            raise InvalidContactUserForm(form)
        try:
            from_user = user
            to_user = (talk.trip.user if from_user.id == talk.from_user.id
                    else talk.from_user)
            subject = talk.trip.get_public_name()
            message_header = (u"%s a annulé la négociation " %
                from_user.username)
                
            if from_user.id == talk.from_user.id:
                message_header += u"à propos de votre annonce %s (%s)." % (
                    talk.trip.name,
                    subject,
                )
            else:
                message_header += (u"à propos de l'annonce %s." %
                    subject)
            send_mail(
                (u"Annonce %s - Annulation de la négociation" %
                    subject),
                u"""Ceci est un message automatique, veuillez ne pas y répondre.

Bonjour %s,

%s
Il semblerait que vous n'ayez pas trouvé de compromis satisfaisant.

Voici la raison de l'annulation donnée par %s:
--------------------------------
%s
--------------------------------

Nous espérons que vous aurez plus de chance lors de votre prochaine négociation.

Cordialement,
L'équipe %s""" % (
                    to_user.username,
                    message_header,
                    from_user.username,
                    form.cleaned_data['message'],
                    settings.PROJECT_NAME
                ),
                settings.FROM_EMAIL, [to_user.email]
            )
            talk.delete()
        except Exception, err:
            transaction.rollback()
            raise err
        else:
            transaction.commit()

    def delete_trip(self, user, trip_id, post_data):
        """Delete a trip
        
        Delete the announce and associated negociations and alert the contact 
        that the negociation has been deleted because of the related announce 
        deletion.
        
        - If the trip doesnt exists, raise a TripDoesNotExist exception
        """
        try:
            trip = Trip.objects.get(pk=trip_id, user=user)
        except Trip.DoesNotExist:
            raise InvalidUser(user)
            
        form = ContactUserForm(post_data)
        if not form.is_valid():
            raise InvalidContactUserForm(form)
            
        for talk in trip.talk_set.all():
            try:
                from_user = user
                to_user = talk.from_user
                subject = talk.trip.get_public_name()
                message_header = u"%s a supprimé son annonce %s" % (
                    from_user.username,
                    subject,
                )
                send_mail(
                    (u"Annonce %s - Suppression de l'annonce et de la "
                        u"négociation" % subject),
                    u"""Ceci est un message automatique, veuillez ne pas y répondre.

Bonjour %s,

%s,
ce qui entraîne la suppression de votre négociation.

Voici la raison de la suppression donnée par %s:
--------------------------------
%s
--------------------------------

Cordialement,
L'équipe %s""" % (
                        to_user.username,
                        message_header,
                        from_user.username,
                        form.cleaned_data['message'],
                        settings.PROJECT_NAME
                    ),
                    settings.FROM_EMAIL, [to_user.email]
                )
            except:
                pass
        trip.delete()
       
    def validate_talk(self, user, talk_id):
        """Validate the negociation talk:
            + create a temporary rating
            + send a mail to the other carpooler
            + delete the negociation
        
        Validation is definitive and bilateral.
        
        - On error, raise an *** exception
        - If the trip doesnt exists, raise a TripDoesNotExist exception
        """
        
        try:
            talk = Talk.objects.get(pk=talk_id)
            from ipdb import set_trace
            set_trace()
        except Talk.DoesNotExist:
            raise TalkDoesNotExist(talk_id)
            
        if (talk.from_user.id != user.id and talk.trip.user.id != user.id):
            raise InvalidUser(user)

        try:
            # Create the temp report
            temp_report = TempReport(
                departure_city=talk.trip.departure_city,
                arrival_city=talk.trip.arrival_city,
                type=talk.trip.trip_type,
                regular=talk.trip.regular,
                date=talk.trip.date,
                interval_min=talk.trip.interval_min,
                interval_max=talk.trip.interval_max,
                dows=talk.trip.dows,
                user1=talk.from_user,
                report1_creation_date=None,
                report1_mark=None,
                report1_comment=None,
                user2=talk.trip.user,
                report2_creation_date=None,
                report2_mark=None,
                report2_comment=None,
            )
            temp_report.save()
            # Send an email
            from_user = user
            to_user = (talk.trip.user if from_user.id == talk.from_user.id
                    else talk.from_user)
            subject = talk.trip.get_public_name()
            send_mail(
            u"Annonce %s - Validation de la négociation" % subject,
            u"""Ceci est un message automatique, veuillez ne pas y répondre.

Bonjour %s,

%s a validé votre négociation.

Bon covoiturage avec %s !""" % (
                    to_user.username,
                    from_user.username,
                    settings.PROJECT_NAME,
                ),
                settings.FROM_EMAIL, [to_user.email]
            )
            # delete the talk
            talk.delete()
        except Exception, err:
            transaction.rollback()
            raise err
        else:
            transaction.commit()

    def _send_message(self, talk, from_user, to_user, message):
        """Send a mail and create a message
        
        """
        subject = talk.trip.get_public_name()
        if from_user.id == talk.from_user.id:
            message_header = u"%s vous a laissé un message " % from_user.username
            message_header += u"à propos de votre annonce %s (%s):""" % (
                talk.trip.name,
                subject,
            )
        else:
            message_header = u"%s vous a répondu à propos de l'annonce %s:" % (
                from_user.username,
                subject,
            )

        msg = Message(
            talk=talk,
            from_user=(from_user.id == talk.from_user.id),
            message=message
        )
        msg.save()
        send_mail(
        u"Annonce %s" % subject,
        u"""Ceci est un message automatique, veuillez ne pas y répondre.

Bonjour %s,

%s

--------------------------------
%s
--------------------------------

Pour lui répondre, vous pouvez continuer à utiliser les services %s:
%s%s#nouveau_message
Ou bien contacter cet utilisateur directement s'il vous a communiqué son 
adresse email ou son numéro de téléphone.

N'oubliez pas de consulter vos négociations en cours:
%s%s

Bon covoiturage avec %s !""" % (
                to_user.username,
                message_header,
                message,
                settings.PROJECT_NAME,
                settings.PROJECT_ROOT_URL,
                reverse('talks:add_message', args=[talk.id]),
                settings.PROJECT_ROOT_URL,
                reverse('talks:list_talks', args=[1]),
                settings.PROJECT_NAME,
            ),
            settings.FROM_EMAIL, [to_user.email]
        )
