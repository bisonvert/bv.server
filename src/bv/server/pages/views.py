# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Views for the page application. the page app contains all pages that doesn't
relies directly on another application.

"""

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.core.mail import send_mail
from django.template import RequestContext, Context, loader
from bv.server.pages.forms import ContactForm, AnonymousContactForm, SUBJECT_CHOICE
from django.conf import settings

def contact(request):
    """Contact Form
    This view is acessible via GET and POST.

    On GET, it displays a form
    On POST, check if the form is valid, sent the mail and redirect to other views

    """
    response_dict = {
        'current_footer_item': 2,
    }

    if request.method == 'POST':
        if request.user.is_authenticated():
            form = ContactForm(request.POST)
        else:
            form = AnonymousContactForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated():
                name = u"%s (%s %s)" % (
                    request.user.username,
                    request.user.first_name if request.user.first_name else "",
                    request.user.last_name if request.user.last_name else ""
                )
                if request.user.email:
                    email = request.user.email
                else:
                    email = request.user.get_profile().validation.email
            else:
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
            subject = SUBJECT_CHOICE[int(form.cleaned_data['subject'])][1]
            send_mail(
                u"[%s] %s" % (subject, form.cleaned_data['title']),
                """
%s dit :

%s
                """ % (name, form.cleaned_data['message']),
                email, [settings.CONTACT_EMAIL]
            )
            return HttpResponseRedirect(reverse('confirm_contact'))
    else:
        if request.user.is_authenticated():
            form = ContactForm()
        else:
            form = AnonymousContactForm()

    response_dict.update({'form': form})

    template = loader.get_template('carpool/contact.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: MEDIA_URL
    
    """
    template = loader.get_template(template_name)
    return HttpResponseServerError(template.render(Context({'MEDIA_URL': settings.MEDIA_URL})))
