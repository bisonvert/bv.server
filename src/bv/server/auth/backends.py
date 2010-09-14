# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Authentication Backend for Ecov"""

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend as DjangoModelBackend

class ModelBackend(DjangoModelBackend):
    """Classe ModelBackend"""
    def authenticate(self, username=None, password=None):
        """Username insensible à la casse pour l'auth"""
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
