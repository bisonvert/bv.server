# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Administration class for account model."""

from django.contrib import admin
from models import ForbiddenUsername

class ForbiddenUsernameAdmin(admin.ModelAdmin):
    list_display = ['username']
    pass

admin.site.register(ForbiddenUsername, ForbiddenUsernameAdmin)
