# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Personalized fields for forms."""

from django.forms import fields
from utils.widgets import FrenchDateInput, SelectableTimeWidget,CheckboxSelectMultipleAsArray
from datetime import time
from django.utils.translation import ugettext as _

import re

FRENCH_DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', # '2006-10-25', '25/10/2006', '25/10/06'
    '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', # '25.10.2006', '25.10.06', '25-10-2006'
    '%d %b %Y',                         # '25 Oct 2006'
    '%d %B %Y',                         # '25 October 2006', 'October 25, 2006'
)

class FrenchDateField(fields.DateField):
    """Represents a french date
    
    Inherit from django DateField form field

    Use french format:
    ::

        FRENCH_DATE_INPUT_FORMATS = (
            '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', # '2006-10-25', '25/10/2006', '25/10/06'
            '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', # '25.10.2006', '25.10.06', '25-10-2006'
            '%d %b %Y',                         # '25 Oct 2006'
            '%d %B %Y',                         # '25 October 2006', 'October 25, 2006'
        )

    """
    widget = FrenchDateInput

    def __init__(self, *args, **kwargs):
        super(FrenchDateField, self).__init__(
            FRENCH_DATE_INPUT_FORMATS, *args, **kwargs
        )

class FrenchDecimalField(fields.DecimalField):
    """Represents a french decimal value
    
    Inherit from django DecimalField
    
    Accept the english format (12.34), or the french one (12,34).

    """
    def clean(self, value):
        """Replace the comma by a dot, and call the validation method from 
        parent class.

        """
        if value:
            value = re.sub(r',', '.', value)
        return super(FrenchDecimalField, self).clean(value)
        
class SelectableTimeField(fields.TimeField):
    widget = SelectableTimeWidget
    
    def clean(self, value):
        """
        Convert the input value to a time if possible. Returns a Python
        datetime.time object.
        """
        if value in ('',None):
            return None
        else:
            return super(SelectableTimeField, self).clean(time(int(value)))
        
class MultipleChoiceField(fields.TimeField):
    widget = SelectableTimeWidget
    
    def clean(self, value):
        """
        Validates that the input can be converted to a time. Returns a Python
        datetime.time object.
        """
        return super(SelectableTimeField, self).clean(time(int(value)))     
