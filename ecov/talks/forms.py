# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Forms for talk module"""

from django.utils.translation import ugettext_lazy as _

from django import forms

class ContactUserForm(forms.Form):
    """Form for contact another user about a carpool announce. Internal instant 
    messaging for negotiations.
    
    This form is used by negotiation initialisation, message add, negotiation
    deletion and announce deletion (if a related negotiation exists)
    """
    message = forms.CharField(
        label=_("* Message:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )
