# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Admin for the "site" module"""

from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from models import FavoritePlace, City, CarType

class FavoritePlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'address', 'design']
    search_fields = ('name', 'city')

admin.site.register(FavoritePlace, FavoritePlaceAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'zipcode', 'insee_code', 'population']
    search_fields = ('name', 'zipcode')

admin.site.register(City, CityAdmin)

class CarTypeAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(CarType, CarTypeAdmin)
