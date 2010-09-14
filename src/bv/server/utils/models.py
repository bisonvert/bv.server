# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Personalized model fields types."""

from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.core import exceptions
from django.utils.datastructures import SortedDict

import re

_R_ARRAY = re.compile('^{(.*)}$')

class DOWArrayField(models.Field):
    """Modelisation of a DOW type (Day Of Week).
    
    Database type: integer[]
    Python type: list
    
    Remark: Have been developed on a postgresql database. Compatibility with 
    other database types has not been tested
    
    """
    __metaclass__ = models.SubfieldBase

    DOWS = [0, 1, 2, 3, 4, 5, 6]

    def __init__(self, *args, **kwargs):
        super(DOWArrayField, self).__init__(*args, **kwargs)

    def is_dow(self, field_data, all_data):
        """Validator.

        Check that:

        + each element of the list is an integer
        + each element of the list is on the list of authorized values

        """
        for value in field_data:
            try:
                if int(value) not in self.DOWS:
                    raise exceptions.ValidationError(_(""
                        "%(day)d is not a valid day of week." % {'day':
                            int(value)}))
            except ValueError:
                raise exceptions.ValidationError(_(""
                    "This list must contain only integers."))

    def db_type(self):
        """Return the column type (the DB one)
        
        """
        return 'integer[]'

    def to_python(self, value):
        """Convert the database returned value into a python type

        """
        if isinstance(value, list):
            return value
        try:
            value_list = _R_ARRAY.match(value).group(1)
        except (AttributeError, TypeError):
            return []
        if not value_list:
            return []
        return value_list.split(',')

    def get_db_prep_value(self, value):
        """reverse of the methode "to_python"."""
        # convert the unicode chars to ints
        value = [int(value) for value in value]
        self.is_dow(value, None)
        value.sort()
        return "{%s}" % ','.join(["%d" % v for v in value])

