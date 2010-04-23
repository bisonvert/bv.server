from django import forms
from django.forms.models import ModelForm
from piston.models import Consumer
from django.utils.translation import ugettext_lazy as _


class CreateOauthAccessForm(forms.ModelForm):
    name = forms.CharField(
        label=_('Name'), 
        help_text=_('The name of your application')
    )
    description = forms.CharField(
        label = _('Desciption'),
        help_text = _('What is your application goal ?'),
        widget=forms.Textarea
    )
    
    class Meta:
        model = Consumer
        fields = ('name', 'description')
