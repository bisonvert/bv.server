# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Forms for accounts module:"""

from django.utils.translation import ugettext_lazy as _

from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.safestring import mark_safe
from django.conf import settings

from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from accounts.models import UserProfile, EmailValidation, ForbiddenUsername
from bv.server.carpool.models import CarType
from bv.server.utils.fields import FrenchDecimalField
from bv.server.utils.widgets import NullBooleanSelect

import re

_MSG_FORMAT_IDENTIFIANT = _("The username must contain at leat 3 valid "
        "characters(alphanumeric characters, ., -, _)")
_REGEXP_LOGIN = r'^[a-zA-Z0-9_\.-]{3,30}$'

_CGU_CHOICE = (
    (1, mark_safe(u"%s <a href=\"/cgu/\">%s</a>" %
        (_("I have read and agree with the"), _("terms and conditions"))
    )),
)
_REMEMBER_ME_CHOICE = (
    (1, _("Remember me")),
)

class RegisterForm(forms.Form):
    """Registering form"""
    email = forms.EmailField(
        label=_("* Email"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    username = forms.RegexField(
        _REGEXP_LOGIN,
        label=_("* Username"),
        help_text=_("at least %(num)d characters") % {'num': 3},
        min_length=3, max_length=30,
        error_message=_MSG_FORMAT_IDENTIFIANT,
    )
    password = forms.CharField(
        label=_("* Password"),
        help_text=_("at least %(num)d characters") % {'num': 6},
        min_length=6, max_length=30,
        widget=forms.widgets.PasswordInput()
    )
    password2 = forms.CharField(
        label=_("* Password (again)"),
        help_text=_("at least %(num)d characters") % {'num': 6},
        min_length=6, max_length=30,
        widget=forms.widgets.PasswordInput()
    )
    cgu = forms.MultipleChoiceField(
        label="",
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple({'class': 'checkbox'}),
        choices=_CGU_CHOICE
    )

    def clean_email(self):
        """
        Email cleaner

        Check that mail isn't already taken by any other user (validated 
        or not).
        """
        if (not User.objects.filter(email__iexact=self.cleaned_data['email'])
                and not EmailValidation.objects.filter(
                    email__iexact=self.cleaned_data['email']
                )):
            return self.cleaned_data['email']
        raise forms.ValidationError(_("Only one account by email address."))

    def clean_username(self):
        """
        Username cleaner

        Check that username isn't already taken, and that is not a forbidden username
        """
        if User.objects.filter(username__iexact=self.cleaned_data['username']):
            raise forms.ValidationError(_("Username already existing."))
        for forbidden_username in ForbiddenUsername.objects.all():
            if re.match(r'(?i)^%s$' % forbidden_username.username,
                    self.cleaned_data['username']):
                raise forms.ValidationError(_("This username is forbidden."))
        return self.cleaned_data['username']

    def clean_password2(self):
        """
        Password2 cleaner (password confirmation)

        Check that password equals password2
        """
        if 'password' not in self.cleaned_data or self.cleaned_data['password2'] == self.cleaned_data['password']:
            return self.cleaned_data['password2']
        raise forms.ValidationError(_("Password does not match."))

    def clean_cgu(self):
        """
        CGU Cleaner

        Check that CGU checkbox is checked
        """
        if self.cleaned_data['cgu']:
            return self.cleaned_data['cgu']
        raise forms.ValidationError(
                _("You have to read and agree with the terms and conditions.")
        )

class AuthenticationForm(BaseAuthenticationForm):
    """Login form"""
    remember_me = forms.MultipleChoiceField(
        label="",
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple({'class': 'checkbox'}),
        choices=_REMEMBER_ME_CHOICE
    )

class NewPasswordForm(forms.Form):
    """
    Form for new password generation. 
    
    Create a new password and send it via mail.
    """
    username = forms.CharField(label=_("* Username"))
    email = forms.EmailField(
        label=_("* Email"),
        widget=forms.widgets.TextInput({'size': '40'})
    )

    def __init__(self, *args, **kwargs):
        """Init user object"""
        self.user = None
        super(NewPasswordForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Username cleaner
        
        Check that given username exists, if so, fetch the mathing one.
        """
        try:
            self.user = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("Unknown user."))
        return self.cleaned_data['username']

    def clean_email(self):
        """
        Email cleaner
        
        Check that given email matches with the user one.
        It's not possible to send a new password to an unchecked user email
        """
        if self.user and self.user.email != self.cleaned_data['email']:
            if (self.user.get_profile().validation
                    and (self.user.get_profile().validation.email
                        == self.cleaned_data['email'])):
                raise forms.ValidationError(
                        _("This email address was not validated, "
                            "impossible to send a new password.")
                )
            else:
                raise forms.ValidationError(
                        _("Email address does not match with username.")
                )
        return self.cleaned_data['email']

class UserProfileForm(ModelForm):
    """User profile edition form"""
    email = forms.EmailField(
        label=_("* Email:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    oldpassword = forms.CharField(
        label=_("Old password:"),
        required=False,
        widget=forms.widgets.PasswordInput()
    )
    newpassword = forms.CharField(
        label=_("New password:"),
        help_text=_("at least %(num)d characters") % {'num': 6},
        required=False,
        min_length=6, max_length=30,
        widget=forms.widgets.PasswordInput()
    )
    newpasswordconfirm = forms.CharField(
        label=_("New password (again):"),
        help_text=_("at least %(num)d characters") % {'num': 6},
        required=False,
        min_length=6, max_length=30,
        widget=forms.widgets.PasswordInput()
    )
    lastname = forms.CharField(
        label=_("Lastname:"),
        required=False,
    )
    firstname = forms.CharField(
        label=_("Firstname:"),
        required=False,
    )
    phone = forms.CharField(
        label=_("Phone number:"),
        required=False,
        max_length=14,
    )
    mobile_phone = forms.CharField(
        label=_("Mobile phone number:"),
        required=False,
        max_length=14,
    )
    home_address = forms.CharField(
        label=_("Address:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '40'})
    )
    home_address2 = forms.CharField(
        label=_("Address complement:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '40'})
    )
    home_zipcode = forms.CharField(
        label=_("Zip code:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '5'})
    )
    home_city = forms.CharField(
        label=_("City:"),
        required=False,
    )
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
    )

    def clean_email(self):
        """
        Email cleaner
        
        Check that given email isn't already defined by another user
        """
        validations = EmailValidation.objects.filter(
                email__iexact=self.cleaned_data['email']
        )
        if self.instance.validation:
            validations = validations.exclude(pk=self.instance.validation.id)
        if not User.objects.filter(
                    email__iexact=self.cleaned_data['email']
                ).exclude(pk=self.instance.user.id) and not validations:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("Only one account by email address."))

    def clean_oldpassword(self):
        """
        Old password cleaner
        
        Check that given oldpassword match
        """
        if self.cleaned_data['oldpassword']:
            user = authenticate(username=self.instance.user.username,
                                password=self.cleaned_data['oldpassword'])
            if not user:
                raise forms.ValidationError(_("Incorrect password."))
        return self.cleaned_data['oldpassword']

    def clean_newpassword(self):
        """
        New password cleaner
        
        check that old password had been given
        """
        if ('oldpassword' in self.cleaned_data
                and not self.cleaned_data['oldpassword']
                and self.cleaned_data['newpassword']):
            raise forms.ValidationError(
                    _("Please enter your old password to modify it.")
            )
        return self.cleaned_data['newpassword']

    def clean_newpasswordconfirm(self):
        """
        Confirmation for new password cleaner
        
        check that both new password and confirmation match
        """
        if ('newpassword' in self.cleaned_data
                and self.cleaned_data['newpassword']
                and (self.cleaned_data['newpassword']
                    != self.cleaned_data['newpasswordconfirm'])):
            raise forms.ValidationError(_("Password does not match."))
        return self.cleaned_data['newpasswordconfirm']


    def clean_phone(self):
        """
        Phone number cleaner
        
        Check that given phone number is in french format 
        """
        if self.cleaned_data['phone']:
            value = re.sub(r'[^0-9]', '', self.cleaned_data['phone'])
            if not re.match(r'^0[1-9][0-9]{8}$', value):
                raise forms.ValidationError(_("Incorrect phone number."))
        return self.cleaned_data['phone']

    def clean_mobile_phone(self):
        """
        Phone number cleaner
        
        Check that given phone number is in french format, and is a mibile
        phone number (begin with 06)
        """
        if self.cleaned_data['mobile_phone']:
            value = re.sub(r'[^0-9]', '', self.cleaned_data['mobile_phone'])
            if not re.match(r'^06[0-9]{8}$', value):
                raise forms.ValidationError(_("Incorrect mobile phone number."))
        return self.cleaned_data['mobile_phone']

    class Meta:
        """
        Meta class
        
        Define used fields and models
        """
        model = UserProfile
        fields = (
            'phone',
            'mobile_phone',
            'home_address',
            'home_address2',
            'home_zipcode',
            'home_city',
            'language',
        )

class UserPreferencesForm(ModelForm):
    """User preferencies form"""
    # default alert by email
    alert = forms.BooleanField(
        label=_("Email alert enabled by default:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    # driver preferences
    driver_km_price = FrenchDecimalField(
        label=_("Asking price by kilometer:"),
        max_digits=7,
        decimal_places=2,
        required=False
    )
    driver_smokers_accepted = forms.NullBooleanField(
        label=_("Smokers accepted:"),
        required=False,
        widget=NullBooleanSelect()
    )
    driver_pets_accepted = forms.NullBooleanField(
        label=_("Pets accepted:"),
        required=False,
        widget=NullBooleanSelect()
    )
    driver_place_for_luggage = forms.NullBooleanField(
        label=_("Place for luggages:"),
        required=False,
        widget=NullBooleanSelect()
    )
    driver_car_type = forms.ModelChoiceField(
        label=_("Car type:"),
        required=False,
        queryset=CarType.objects.all(),
    )
    driver_seats_available = forms.IntegerField(
        label=_("Seat number by default:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '5'})
    )
    # passenger preferences
    passenger_max_km_price = FrenchDecimalField(
        label=_("Maximum price by kilometer:"),
        max_digits=7,
        decimal_places=2,
        required=False
    )
    passenger_smokers_accepted = forms.BooleanField(
        label=_("Smokers accepted first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_pets_accepted = forms.BooleanField(
        label=_("Pets accepted first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_place_for_luggage = forms.BooleanField(
        label=_("Place for luggages first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_car_type = forms.ModelChoiceField(
        label=_("Car type first:"),
        required=False,
        queryset=CarType.objects.all(),
    )
    passenger_min_remaining_seats = forms.IntegerField(
        label=_("Minimum remaining seats:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '5'})
    )

    class Meta:
        """
        Meta class for user preferences form
        
        Define used fields and models
        """
        model = UserProfile
        exclude = (
            'user',
            'phone',
            'mobile_phone',
            'home_address',
            'home_address2',
            'home_zipcode',
            'home_city',
            'validation',
            'language',
        )
