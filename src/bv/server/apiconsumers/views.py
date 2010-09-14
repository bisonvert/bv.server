# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response as render, get_object_or_404, \
        redirect
from django.conf import settings

from piston.models import Consumer
from piston.forms import OAuthAuthenticationForm
from apiconsumers.forms import CreateOauthAccessForm

@login_required
def create_consumer(request):
    """Display the form to make a API access demand.

    Once the API key has been generated, send an email to a specified user, 
    wich have the power to validate the API consumer.
    
    """
    if request.POST:
        form = CreateOauthAccessForm(data=request.POST)
        if form.is_valid():
            model = form.save()
            model.user = request.user
            model.generate_random_codes()
            send_mail(_('New API demand on %(project_name)s') % {'project_name' : settings.PROJECT_NAME},
                _("""A new API consumer request is available on
%(project_name)s. Here are the informations about it:

Consumer name: %(consumer_name)s
Description: %(consumer_description)s

You can allow this consumer by going on the following link: %(validate_consumer_url)s.

Thanks""" % {
    'project_name': settings.PROJECT_NAME,
    'consumer_name': model.name,
    'consumer_description': model.description,
    'validate_consumer_url': "%s%s" % (request.build_absolute_uri('/').strip('/'), reverse('apiconsumers:validate', args=[model.id]))
}), settings.FROM_EMAIL, [settings.CONTACT_EMAIL], fail_silently=False)
            return redirect('apiconsumers:list')
    else:    
        form = CreateOauthAccessForm()
    
    return render('create_consumer.html', {
        'form': form,
        'apiconsumers' : True,
    }, context_instance=RequestContext(request))

@login_required
def list_consumers(request):
    """List the API access for the connected user
    
    """
    consumers = Consumer.objects.filter(user=request.user)
    
    return render('list_consumers.html', {
        'consumers': consumers,
        'apiconsumers' : True,
    }, context_instance=RequestContext(request))
    
def oauth_auth_view(request, token, callback, params):
    form = OAuthAuthenticationForm(initial={
        'oauth_token': token.key,
        'oauth_callback': token.get_callback_url() or callback,
      })

    return render('authorize_token.html',{
        'form': form,  
        'apiconsumers' : True,
    }, context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff == True)
def validate_consumer(request, consumer_id):
    """Activate an already existing consumer"""
    consumer = get_object_or_404(Consumer, pk=consumer_id) 
    consumer.status = "accepted"
    consumer.save()
    send_validation_notification(consumer)
    return redirect('apiconsumers:pending')

@user_passes_test(lambda u: u.is_staff == True)
def list_pending_consumers(request):
    """List all pending requests of consumer creation."""
    consumers = Consumer.objects.filter(status='pending')
    return render('list_pending_consumers.html',{
        'consumers': consumers,
        'apiconsumersadmin' : True,
    }, RequestContext(request))

@user_passes_test(lambda u: u.is_staff == True)
def validate_all_pending_consumers(request):
    for consumer in Consumer.objects.filter(status='pending'):
        consumer.status = 'acccepted'
        consumer.save()
        send_validation_notification(consumer)
    return redirect('apiconsumers:pending')

def send_validation_notification(consumer):
    """send a mail to the user the token belongs to"""
    subject = _("Your OAuth API consumer request for %(project_name)s has been accepted" % {'project_name': settings.PROJECT_NAME})
    content = _(u"""We are pleased to annonce you that your API consumer request for %(project_name)s has been accepted by an administrator.

Here are the informations about the consumer:

    Name: %(name)s
    Description: %(description)s
    Consumer key: %(key)s
    Consumer secret: %(secret)s

Now, please refer to the informations available at %(api_url)s for more informations.

Yours, 
The %(project_name)s team.
""" % {
    'project_name': settings.PROJECT_NAME,
    'name': consumer.name,
    'description': consumer.description,
    'key': consumer.key, 
    'secret': consumer.secret,
    'api_url': settings.PROJECT_ROOT_URL,
})
    send_mail(subject, content, settings.FROM_EMAIL,
        [settings.FROM_EMAIL],consumer.user.email)
