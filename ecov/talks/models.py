# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from django.contrib.auth.models import User

from carpool.models import Trip

import datetime

class Talk(models.Model):
    """Talk (Negociation).
    
    A negotiation is described by:

    + trip (ForeignKey on Trip): announce
    + from _user
    + creation_date

    Negotiation (talk) is initiated by a "from_user" abount an announce of
    another carpooler (trip)

    The negotiation contains a list of messages. To fetch the list of messages:
        talk.message_set.all()
    """
    # talk about this trip
    trip = models.ForeignKey(Trip)
    # user who initializes the talk
    from_user = models.ForeignKey(User)

    creation_date = models.DateTimeField()

    def save(self):
        """Add the create date if this is a negociation. 

        """
        if not self.id:
            self.creation_date = datetime.datetime.now()
        super(Talk, self).save()

    class Meta:
        """Meta class

        Define a unicity constraint (a carpooler can only initiate one talk by 
        announce
        """
        unique_together = (
            # a user can create only one talk per trip
            ("trip", "from_user"),
        )

class Message(models.Model):
    """Message

    A message is described by:

    + talk (ForeignKey on talk)
    + from_user (Boolean): True if the carpooler (talk.from_user) had sent the 
    message
    + date: date of the message
    + message: content.

    """
    talk = models.ForeignKey(Talk)
    from_user = models.BooleanField()
    date = models.DateTimeField()
    message = models.TextField()

    def save(self):
        """Fill in the date field 
        call the parent save() method
        """
        if not self.id:
            self.date = datetime.datetime.now()
        super(Message, self).save()
