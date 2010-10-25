# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""views for account module"""

from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.conf import settings

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response

from django.db import transaction
from django.core.mail import send_mail

from bv.server.accounts.forms import RegisterForm, AuthenticationForm, NewPasswordForm
from bv.server.accounts.forms import UserProfileForm, UserPreferencesForm
from bv.server.accounts.models import UserProfile

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """"Default contrib.auth login view, modified to use a specific form, and to
    support "remember me" checkbox
    
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            request.session[settings.PERSISTENT_SESSION_KEY] = bool(
                        form.cleaned_data['remember_me']
            )
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request)
    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
login = never_cache(login)

@transaction.commit_manually
def new_password(request):
    """Gererate a new user password and send mail containing the newly 
    generated password to the user.

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)
    
    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    """
    response_dict = {
        'accounts': True
    }

    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            try:
                password = User.objects.make_random_password(length=8)
                form.user.set_password(password)
                form.user.save()
                send_mail(
                    u"%s - Nouveau mot de passe" % settings.PROJECT_NAME,
                    u"""
Bonjour %s,

Vous nous avez demandé de renouveler votre mot de passe.
C'est donc chose faite, votre nouveau mot de passe est: %s
Il est volontairement compliqué, n'hésitez pas à le modifier dans votre
profil.

Bon covoiturage avec %s !""" % (
                        form.user.username,
                        password,
                        settings.PROJECT_NAME
                    ),
                    settings.FROM_EMAIL,
                    [form.cleaned_data['email']]
                )
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()
                return HttpResponseRedirect(reverse('accounts:confirm_new_password'))
    else:
        form = NewPasswordForm()

    response_dict.update({'form': form})

    template = loader.get_template('accounts/new_password.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@transaction.commit_manually
def register(request):
    """Create the new user, and connect it automatically. Send him a validation 
    email, in order to allow him to validate his mail address.

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)
    """
    response_dict = {
        'accounts': True
    }

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                response_dict.update({'ok_cgu': True})
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    '',
                    form.cleaned_data['password']
                )
                user.save()
                userprofile = UserProfile(user=user)
                userprofile.save()
                userprofile.set_email(form.cleaned_data['email'])
                # auto login after registration
                user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'])
                if user:
                    from django.contrib.auth import login
                    login(request, user)
                    request.session[settings.PERSISTENT_SESSION_KEY] = False

                _send_validation_mail(request, user, True)
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()
                return HttpResponseRedirect(reverse('accounts:confirm_registration'))
    else:
        form = RegisterForm()
    response_dict.update({'form': form})

    template = loader.get_template('accounts/register.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def validate_email(request, key):
    """Validate Email
    
    Check that the key is valid, and validate the user email if so.
    """
    response_dict = {
        'accounts': True
    }

    try:
        userprofile = UserProfile.objects.get(validation__key=key)
        userprofile.user.email = userprofile.validation.email
        userprofile.user.is_valid = True
        userprofile.user.save()
        validation = userprofile.validation
        userprofile.validation = None
        userprofile.save()
        validation.delete()
    except UserProfile.DoesNotExist:
        response_dict.update({'notfound': True})

    template = loader.get_template('accounts/validate_email.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def my_account(request):
    """Home of the "My account" section. Redirect to profile editing"""
    return edit_profile(request)

@login_required
@transaction.commit_manually
def edit_profile(request):
    """Update user profile. If the mail has been changed, send a validation mail

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.

    Transaction: manual commit (decorator transaction.commit_manually) allows us
    to manage mail sending errors.
    """
    response_dict = {
        'accounts': True,
        'current_nav_item': 1,
    }

    user = request.user
    userprofile = user.get_profile()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=userprofile)
        if form.is_valid():
            try:
                userprofile = form.save(commit=False)
                userprofile.save()
                has_validation = (userprofile.validation != None)
                changed = userprofile.set_email(form.cleaned_data['email'])
                if (form.cleaned_data['oldpassword']
                        and form.cleaned_data['newpassword']
                        and form.cleaned_data['newpasswordconfirm']):
                    user.set_password(form.cleaned_data['newpasswordconfirm'])
                user.first_name = form.cleaned_data['firstname']
                user.last_name = form.cleaned_data['lastname']
                user.save()
                response_dict.update({'save_confirmation': True})
                if changed:
                    if has_validation:
                        response_dict.update({'validation_key_not_valid': True})
                    _send_validation_mail(request, user)
            except Exception, err:
                transaction.rollback()
                raise err
            else:
                transaction.commit()
    else:
        data = {
            'email': (user.email if user.email and not userprofile.validation
                else userprofile.validation.email),
            'firstname': user.first_name,
            'lastname': user.last_name,
            'home_zipcode': userprofile.home_zipcode,
        }
        form = UserProfileForm(initial=data, instance=userprofile)
    response_dict.update({'form': form})

    template = loader.get_template('accounts/edit_profile.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def edit_preferences(request):
    """Edit user preferences

    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users.
    """
    response_dict = {
        'accounts': True,
        'current_nav_item': 2,
    }

    userprofile = request.user.get_profile()

    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=userprofile)
        
        if form.is_valid():
            userprofile = form.save(commit=False)
            userprofile.save()
            response_dict.update({'save_confirmation': True})
    else:
        form = UserPreferencesForm(instance=userprofile)
    response_dict.update({'form': form})

    template = loader.get_template('accounts/edit_preferences.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

@login_required
def edit_contact(request):
    """Vue d'édition des contacts. NON UTILISEE POUR LE MOMENT."""
    response_dict = {
        'current_item': 12,
    }

    template = loader.get_template('accounts/edit_contact.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def _send_validation_mail(request, user, first_validation=False):
    """Fonction d'envoi d'un email de validation."""

    userprofile = user.get_profile()
    if first_validation:
        title = u"Bienvenue sur %s %s," % (settings.PROJECT_NAME, user.username)
    else:
        title = u"Bonjour %s," % user.username
    send_mail(
        u"%s - Validation de votre adresse email" % settings.PROJECT_NAME,
        title + u"""

Afin de valider votre adresse email, veuillez cliquer sur le lien ci-dessous:
%s%s

(Si le lien ne fonctionne pas, copiez-le puis collez-le dans le barre d'adresse de votre navigateur)

Bon covoiturage avec %s !""" % (
            request.build_absolute_uri('/').strip('/'),
            reverse(
                'accounts:validate_email',
                args=[userprofile.validation.key]
            ),
            settings.PROJECT_NAME
        ),
        settings.FROM_EMAIL,
        [userprofile.validation.email]
    )
