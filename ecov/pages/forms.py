# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Forms for site module."""

from django.utils.translation import ugettext_lazy as _
from django import forms

SUBJECT_CHOICE = (
    ('', '---------'),
    (1, _("Report a bug")),
    (2, _("Suggestions")),
    (3, _("Comments")),
    (4, _("Encouragements")),
    (5, _("Other")),
)

class AnonymousContactForm(forms.Form):
    """Anonymous contact form.

    Contains:

    + user name
    + user email
    + subject
    + title
    + message

    """
    name = forms.CharField(
        label=_("* Firstname / Lastname:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    email = forms.EmailField(
        label=_("* Email:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    subject = forms.ChoiceField(
        label=_("* Subject:"),
        choices=SUBJECT_CHOICE,
    )
    title = forms.CharField(
        label=_("* Title:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    message = forms.CharField(
        label=_("* Message:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )

class ContactForm(forms.Form):
    """Contact form for logged users

    Contains:

    + subject
    + title
    + message

    """
    subject = forms.ChoiceField(
        label=_("* Subject:"),
        choices=SUBJECT_CHOICE,
    )
    title = forms.CharField(
        label=_("* Title:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    message = forms.CharField(
        label=_("* Message:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )
