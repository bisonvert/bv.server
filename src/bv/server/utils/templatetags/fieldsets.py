# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Fieldset related templatetags

"""
import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict

register = template.Library()

class FieldSetNode(template.Node):
    def __init__(self, fields, variable_name, form_variable):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):
        
        form = template.Variable(self.form_variable).resolve(context)
        new_form = copy.copy(form)
        new_form.fields = SortedDict([(key, form.fields[key]) for key in self.fields if key in form.fields])

        context[self.variable_name] = new_form

        return u''

@register.tag
def get_fieldset(parser, token):
    """Render given fields of a form as a subform.
    
    Usage ::
        
        {% get_fieldset name,password,etc as newform from form %}
    
    """
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])
    return FieldSetNode(fields.split(','), variable_name, form)
