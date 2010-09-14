# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Forms for rating module"""

from django.utils.translation import ugettext_lazy as _

from django import forms

_MARK_CHOICE = [(mark, mark) for mark in range(0, 6)]
_MARK_CHOICE = (
    ('', '-------------------'),
    (0, _("%(int)d (minimum)") % {'int': 0}),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, _("%(int)d (maximum)") % {'int': 5}),
)

class ReportForm(forms.Form):
    """Reporting form"""
    mark = forms.ChoiceField(
        label=_("* Mark:"),
        choices=_MARK_CHOICE,
    )
    comment = forms.CharField(
        label=_("* Comment:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )
