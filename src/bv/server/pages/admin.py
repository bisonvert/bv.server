# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django import forms
from django.contrib import admin
from bv.server.pages.models import EnhancedFlatPage, Category
from django.utils.translation import ugettext_lazy as _


class FlatPageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/]+$',
        help_text = _("Example: '/about/contact/'. Make sure to have leading"
                      " and trailing slashes."),
        error_message = _("This value must contain only letters, numbers,"
                          " underscores, dashes or slashes."))

    class Meta:
        model = EnhancedFlatPage


class FlatPageAdmin(admin.ModelAdmin):
    form = FlatPageForm
    fieldsets = (
        (None, {'fields': ('url', 'link_name', 'title', 'content', 'order', 'category', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')

admin.site.register(EnhancedFlatPage, FlatPageAdmin)
admin.site.register(Category)