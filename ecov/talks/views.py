# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Views for talk app."""

from django.utils.translation import ugettext_lazy as _

from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.simple import direct_to_template

from django.conf import settings

from django.db import transaction
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from carpool.models import Trip
from talks.models import Talk, Message
from talks.forms import ContactUserForm
from rating.models import TempReport
from utils.paginator import PaginatorRender

_TALK_PG = [10, 20, 50]

@login_required
def list_talk(request, page=1):
    """List of talks (negotiations) for logged user
    
    Paginated list, with ordering on columns.
    
    This view is only accessible by connected users.
    
    """
    ordering = {
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
    pgnum = _TALK_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _TALK_PG:
                pgnum = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pgnum
    get_url = '?pg=%d&order=%s' % (pgnum, order)

    oargs = ordering[order]

    paginator = PaginatorRender(
        Talk.objects.select_related().filter(
            Q(from_user=request.user) | Q(trip__user=request.user)
        ).extra(
            select={
                'type': 'CASE WHEN carpool_trip.demand_id IS NULL THEN 0 '
                'WHEN carpool_trip.offer_id IS NULL THEN 1 ELSE 2 END'
            }
        ).order_by(*oargs),
        page,
        pgnum,
        allow_empty_first_page=True,
        extra_context = {
            'current_item': 13,
            'paginations': _TALK_PG,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
            'order': order,
        }
    )
    return paginator.render(request, 'talks/list_talk.html')

@login_required
@transaction.commit_manually
def contact_user(request, trip_id):
    """Create a new negociation about an announce
    
    Create the negotiation, the message, send a mail to the user trip, and
    redirect user to the list of negociations
    
    If a negociation already exists for this announce and this user (the logged 
    one), redirect the user to the add message view
    
    If one of the email field is empty, redirect user to the contact error view

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.

    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    
    """
    trip = get_object_or_404(Trip, pk=trip_id)
    try:
        talk = Talk.objects.get(trip=trip, from_user=request.user)
        return HttpResponseRedirect(
            "%s#nouveau_message" % reverse(
                'talks:add_message',
                args=[talk.id]
            )
        )
    except Talk.DoesNotExist:
        pass

    if request.user.email == "" or trip.user.email == "":
        # email not validated
        return HttpResponseRedirect(reverse('talks:error_contact'))

    from_user = request.user
    to_user = trip.user
    subject = _("Trip %(trip_public_name)s") % {
        'trip_public_name': trip.get_public_name()
    }
    if request.method == 'POST':
        form = ContactUserForm(request.POST)
        if form.is_valid():
            try:
                talk = Talk(
                    trip=trip,
                    from_user=from_user
                )
                talk.save()
                _send_message(
                    request,
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
                return HttpResponseRedirect(
                    reverse('talks:list_talks', args=[1])
                )
    else:
        form = ContactUserForm()

    response_dict = {
        'current_item': 13,
        'form': form,
        'from_user': from_user,
        'to_user': to_user,
        'subject': subject,
    }

    template = loader.get_template('talks/contact_user.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def error_contact(request):
    """Display an explicative message when one of the user's email has not been 
    validated yet
    
    """
    if request.user.email == "":
        error_reason = _("Your email is not yet validated.")
    else:
        error_reason = _("The carpool user email is not yet validated.")

    response_dict = {
        'current_item': 13,
        'error_reason': error_reason,
    }

    template = loader.get_template('talks/error_contact.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
@transaction.commit_manually
def add_message(request, talk_id):
    """Add a message to the negotiation talk, send a mail and redirect user
    to the talks list

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.

    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    """
    talk = get_object_or_404(Talk, pk=talk_id)
    if (talk.from_user.id != request.user.id
            and talk.trip.user.id != request.user.id):
        raise Http404

    from_user = request.user
    to_user = (talk.trip.user if from_user.id == talk.from_user.id
            else talk.from_user)
    subject = _("Trip %(trip_public_name)s") % {
        'trip_public_name': talk.trip.get_public_name()
    }
    if request.method == 'POST':
        form = ContactUserForm(request.POST)
        if form.is_valid():
            try:
                _send_message(
                    request,
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
                return HttpResponseRedirect(
                    reverse('talks:list_talks', args=[1])
                )
    else:
        form = ContactUserForm()

    response_dict = {
        'current_item': 13,
        'form': form,
        'from_user': from_user,
        'to_user': to_user,
        'subject': subject,
        'talk': talk,
    }

    template = loader.get_template('talks/contact_user.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
@transaction.commit_manually
def cancel_talk(request, talk_id):
    """Cancel the negotiation talk
    
    Delete the negociation talk and associated messages, send a mail to the other 
    user and redirect to the talk's list
    
    Canceling a negociation talk must have a reason. So, we use the contact form
    
    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.

    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    """
    talk = get_object_or_404(Talk, pk=talk_id)
    if (talk.from_user.id != request.user.id
            and talk.trip.user.id != request.user.id):
        raise Http404

    if request.method == 'POST':
        form = ContactUserForm(request.POST)
        if form.is_valid():
            try:
                from_user = request.user
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
                return HttpResponseRedirect(
                    reverse('list_talks', args=[1])
                )
    else:
        form = ContactUserForm()

    response_dict = {
        'current_item': 13,
        'form': form,
    }

    template = loader.get_template('talks/cancel_talk.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def delete_trip(request, trip_id):
    """Delete an announce (a trip) 
    
    Delete the announce and associated negociations and alert the contact that 
    the negociation has been deleted because of the related announce deletion.

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.
    """
    trip = get_object_or_404(Trip, pk=trip_id, user=request.user)

    if request.method == 'POST':
        form = ContactUserForm(request.POST)
        if form.is_valid():
            for talk in trip.talk_set.all():
                try:
                    from_user = request.user
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
            return HttpResponseRedirect(
                reverse('carpool:list_user_trips', args=[1])
            )
    else:
        form = ContactUserForm()

    response_dict = {
        'current_item': 10,
        'form': form,
    }

    template = loader.get_template('talks/delete_trip.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
@transaction.commit_manually
def validate_talk(request, talk_id):
    """Validate the negociation talk:
        + create a temporary rating
        + send a mail to the other carpooler
        + delete the negociation
    
    Validation is definitive and bilateral.

    On success, redirect user to the confirmation view
    On error, display an explicative message

    This view is only accessible by connected users.

    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    """
    talk = get_object_or_404(Talk, pk=talk_id)
    if (talk.from_user.id != request.user.id
            and talk.trip.user.id != request.user.id):
        raise Http404

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
        from_user = request.user
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
        return HttpResponseRedirect(
            reverse('talks:confirm_talk_validation')
        )

@login_required
def confirm_talk_validation(*args, **kwargs):
    return direct_to_template(*args, **kwargs)

def _send_message(request, talk, from_user, to_user, message):
    """Private function for  talks module.

    Send a mail and create a message. Used in:
        + talks.views.contact_user 
        + talks.views.add_message.
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
            request.build_absolute_uri('/').strip('/'),
            reverse('talks:add_message', args=[talk.id]),
            request.build_absolute_uri('/').strip('/'),
            reverse('talks:list_talks', args=[1]),
            settings.PROJECT_NAME,
        ),
        settings.FROM_EMAIL, [to_user.email]
    )
