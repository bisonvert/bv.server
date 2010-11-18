# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""
Account module Models
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from bv.server.carpool.models import CarType

from random import choice

_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWYXZabcdefghijklmnopqrstuvwxyz0123456789'


class ForbiddenUsername(models.Model):
    """
    Forbidden Usernames
    
    Define forbidden usernames when registering, work with regexps, see 
    registering form for more details.
    
    For instance: "admin", "administrator", "webmaster", "bisonvert", ...
    """
    username = models.CharField(max_length=30)

    def __unicode__(self):
        """Unicode representation for this model"""
        return u"%s" % self.username

    class Meta:
        """Meta class"""
        verbose_name = "Identifiant interdit"
        verbose_name_plural = "Identifiants interdits"
        ordering = ['username']

class EmailValidation(models.Model):
    """Email validation"""
    key = models.CharField(max_length=50, unique=True)
    email = models.EmailField()

class UserProfile(models.Model):
    """User profile"""
    user = models.ForeignKey(User, unique=True)
    phone = models.CharField(max_length=14, null=True)
    mobile_phone = models.CharField(max_length=14, null=True)
    home_address = models.CharField(max_length=255, null=True)
    home_address2 = models.CharField(max_length=255, null=True)
    home_zipcode = models.CharField(max_length=16, null=True)
    home_city = models.CharField(max_length=255, null=True)
    # général preferences
    alert = models.BooleanField(default=False)
    # driver preferences
    driver_km_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )
    driver_smokers_accepted = models.NullBooleanField()
    driver_pets_accepted = models.NullBooleanField()
    driver_place_for_luggage = models.NullBooleanField()
    driver_car_type = models.ForeignKey(
        CarType,
        null=True,
        related_name='driver_car_type_set'
    )
    driver_seats_available = models.PositiveIntegerField(null=True)
    # passenger preferences
    passenger_max_km_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )
    passenger_smokers_accepted = models.BooleanField(default=False)
    passenger_pets_accepted = models.BooleanField(default=False)
    passenger_place_for_luggage = models.BooleanField(default=False)
    passenger_car_type = models.ForeignKey(
        CarType,
        null=True,
        related_name='passenger_car_type_set'
    )
    passenger_min_remaining_seats = models.PositiveIntegerField(null=True)
    # user validation
    validation = models.ForeignKey(EmailValidation, null=True)
    # user i18n
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, 
        default='fr', null=True)

    def set_email(self, email):
        """Email editing:
        Here are the three different use cases for this method:

        + the given email matches to user.email and user.validation, remove
        the validation
        + user.validation exists: update email and key
        + user.validation doesn't exists, create it
        """
        if self.user.email and self.user.email == email:
            # email does not change
            if self.validation:
                validation = self.validation
                self.validation = None
                self.save()
                validation.delete()
            return False
        key = ''.join([choice(_ALPHABET) for i in range(50)])
        if self.validation:
            if self.validation.email == email:
                # email not yet validated
                return False
            self.validation.key = key
            self.validation.email = email
            self.validation.save()
        else:
            validation = EmailValidation(key=key, email=email)
            validation.save()
            self.validation = validation
        self.save()
        return True
