# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Personalized widgets for forms."""

from itertools import chain
from django.forms import widgets
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.forms.util import flatatt


import datetime

class NullBooleanSelect(widgets.Select):
    """Select for a boolean
    
    Display a select input, with a choice for Yes, No or nothing ("---")
    
    """
    def __init__(self, attrs=None):
        choices = (
            (u'1', u'----------'),
            (u'2', _('Yes')),
            (u'3', _('No'))
        ) ## First choice changed
        super(NullBooleanSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=None):
        """Returns this Widget rendered as HTML, as a Unicode string."""
        if choices is None:
            choices = ()
        try:
            value = {True: u'2', False: u'3', u'2': u'2', u'3': u'3'}[value]
        except KeyError:
            value = u'1'
        return super(NullBooleanSelect, self).render(name, value, attrs,
                choices)

    def value_from_datadict(self, data, files, name):
        """Returns the value of the widget. None if it's not provided.

        """
        value = data.get(name, None)
        return {u'2': True, u'3': False, True: True, False: False}.get(value,
                None)

class FrenchDateInput(widgets.TextInput):
    """French TextInput widget
    
    To use with a field of type FrenchDateField (see utils.fields).
    Render a calendar thanks to javascript

    """
    def __init__(self, attrs=None):
        super(FrenchDateInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        """Returns this Widget rendered as HTML, as a Unicode string."""
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value:
            if isinstance(value, datetime.date):
                value = value.strftime("%d/%m/%Y")
            final_attrs['value'] = value

        if final_attrs.has_key('calendar'):
            if final_attrs['calendar']:
                return (u"<input%s />"
                        " <script language='javascript'>"
                        " var inp = document.getElementById('%s');"
                        "addCalendar(inp, '%s', 'french');"
                        "</script>" % (
                            widgets.flatatt(final_attrs),
                            final_attrs['id'],
                            final_attrs['calendar_class'],
                        ))

        return (mark_safe("<input%s />" % widgets.flatatt(final_attrs)))

class AutoCompleteTextInput(widgets.TextInput):
    """AutoComplete Text Input. 
    
    Widget that makes AJAX autocompletion."""
    def render(self, name, value, attrs=None):
        """Returns this Widget rendered as HTML, as a Unicode string."""
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return (mark_safe('<input%s />'
            '<div id="%s_autocomplete" class="autocomplete" '
            'style="display:none;"></div>' % (
                widgets.flatatt(final_attrs),
                final_attrs['id'],
            )
        ))

class SelectableTimeWidget(widgets.Select):
    """ Displays a list of hours. (24)

    """
    def render(self, name, value, attrs=None, choices=([('', ' -- ')] + 
        [(hour,str(hour).zfill(2) + 'h') for hour in range(0, 24)])):
        """Returns this Widget rendered as HTML, as a Unicode string."""
        if isinstance(value, datetime.time):
            value = value.hour    
        return super(SelectableTimeWidget, self).render(name, value, attrs,
                choices)

class CheckboxInput(widgets.CheckboxInput):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        try:
            result = self.check_test(value)
        except: # Silently catch exceptions
            result = False
        if result:
            final_attrs['checked'] = 'checked'
        if (value not in ('', None)) and str(value) not in ('False', 'True'):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))
    
class CheckboxSelectMultipleAsArray(widgets.SelectMultiple):
    """ Displays the days of week in an array, with the ability to select
    each one, with checkboxes
    
    """
    def render(self, name, value, attrs=None, choices=()):
        """
        >>> w = CheckboxSelectMultipleAsArray()
        >>> w.render(name='dows',value=[u'0', u'1', u'2', u'3', u'4'],attrs={'id': u'id_dows'},choices=((0,"test"),(1,"toto"),(2,"tutu"),(3,"titi")))
u'<table>\n<thead><tr>\n<th><label for="id_dows_0">test</label></th>\n<th><label for="id_dows_1">toto</label></th>\n<th><label for="id_dows_2">tutu</label></th>\n<th><label for="id_dows_3">titi</label></th>\n</tr></thead><tbody>\n<td><input type="checkbox" name="dows" value="0" id="id_dows_0" /></td>\n<td><input type="checkbox" name="dows" value="1" id="id_dows_1" /></td>\n<td><input type="checkbox" name="dows" value="2" id="id_dows_2" /></td>\n<td><input type="checkbox" name="dows" value="3" id="id_dows_3" /></td>\n</tbody></table>'
        
        """
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        str_values = set([force_unicode(v) for v in value])
        output = [u'<table>']
        output.append(u'<thead><tr>')        
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<th><label%s>%s</label></th>' % (label_for, option_label))
        output.append(u'</tr></thead><tbody>')
        
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            
            cb = CheckboxInput(final_attrs, check_test=lambda v: v in value)
            rendered_cb = cb.render(name, option_value)
            output.append(u'<td>%s</td>' % (rendered_cb))
            
        output.append(u'</tbody></table>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)
    
