# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.contrib.flatpages.models import FlatPage as BaseFlatPage
from django.db import models    
from django.utils.translation import ugettext_lazy as _

class Category(models.Model):
    """Represents a category for the page. A page can only have one
    category
    
    """
    name = models.CharField(_('name'), max_length=200)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __unicode__(self):
        return self.name
    
class EnhancedFlatPage(BaseFlatPage):
    """Extends the base FlatPage model adding order and category reference
    
    """    
    category = models.ForeignKey(Category, blank=True)
    order = models.IntegerField(blank=True)
    link_name = models.CharField(_('link name'), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('order',)

