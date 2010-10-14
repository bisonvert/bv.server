# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Models for the rating module

Principles:

A (carpool) user can assess other users and can be evaluated by other users.

An assess is a mark from 0 to 5, plus a comment, and can only be delivered 
following a finished (and validated) negociation. After the trip.

When the negociation is validated by one of the two user, we create a temp
evaluation, wich contains all information to be selfmanaged (temp evaluation
doesnt depends on a negociation or an announce)

This temp evaluation is writable (adding the mark and comment) after a certain
amount of time.

Once a rating has been done, it's not possible to edit it.

this temp assessment is destructed once the two users have filled the 
assessement OR after a certain amount of time.

Temporary assessment aren't used in the average calculation of an user

When a temporary assessement is destroyed, we transform it into a public mark.

Consequences: an user have a list of marks and comments, that are the result of
the destruction and transormation process of temporary assessements.
"""

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from bv.server.carpool.models import Trip
from bv.server.carpool.misc import get_mark_imgs
from bv.server.utils.models import DOWArrayField

import datetime

class Report(models.Model):
    """Objet Report (Assessement)

    An assessement is described by: 

    + user: evaluated carpool user
    + from_user: the evaluating user
    + creation_date: creation date of the assessement.
    + mark: mark from 0 to 5.
    + comment
    """
    user = models.ForeignKey(User, related_name='report_user_set')
    from_user = models.ForeignKey(User, related_name='report_from_user_set')
    creation_date = models.DateField()
    mark = models.PositiveSmallIntegerField()
    comment = models.TextField()

    def get_mark(self):
        """Return the list of "img" tag wich represents the assessement mark.
        To be usen in templates
        """
        return get_mark_imgs(self.mark)

class TempReportQuerySet(models.query.QuerySet):
    """QuerySet for TempReport."""
    def get_user_tempreports(self, user):
        """Returns the list of temporary assessment of an user"""
        return self.filter(Q(user2=user) & Q(report2_mark__isnull=True)
                | Q(user1=user) & Q(report1_mark__isnull=True))

    def get_not_opened_tempreports(self):
        """Return a list of temporary non opened assessments"""
        today = datetime.date.today()
        return self.filter(start_date__gt=today)

    def get_opened_tempreports(self):
        """Return a list of temporary opened assessments"""
        today = datetime.date.today()
        return self.filter(start_date__lte=today, end_date__gte=today)

    def get_closed_tempreports(self):
        """return a list of all closed assessements"""
        today = datetime.date.today()
        return self.filter(end_date__lt=today)

class TempReportManager(models.Manager):
    """Temp report manager

    From http://www.djangosnippets.org/snippets/562/

    """
    def get_query_set(self):
        """Renvoie le QuerySet pour TempReport."""
        model = models.get_model('rating', 'TempReport')
        return TempReportQuerySet(model)

    def __getattr__(self, attr, *args):
        """Pour enchaîner les méthodes des Manager/QuerySet."""
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class TempReport(models.Model):
    """Temporary report (assessement)
    
    a temporary assessement is described by:
    
    Global data:
    + departure_city
    + arrival_city
    + type: route type (offer, demand, both)
    + creation_date
    + start_date : start date for mark reporting
    + end_date : end date form mark reporting
    
    Time related data:
    + regular: define if it's a regular route or not
    + date : departure date (null if regular = true)
    + interval_min : minimum date interval
    + interval_max: maximum date interval
    + dows: days of weeks (used on regular routes)
    
    Assessement made by the first carpooler (arbitrarily, we choose the one wich
    have initiated the talk) :
    + user1: user wich evaluate
    + report1_creation_date
    + report1_mark
    + report1_comment
    
    Assessement made by the second carpooler (arbitrarily, we choose the annouce
    author) :
    + user2
    + report2_creation_date
    + report2_mark
    + report2_comment
    """
    REGULAR_TRIP_DELAY = 15
    PONCTUAL_TRIP_DELAY = 1
    CLOSE_DELAY = 15

    departure_city = models.CharField(max_length=200)
    arrival_city = models.CharField(max_length=200)
    type = models.PositiveIntegerField(choices=Trip.TYPE_CHOICES)

    regular = models.BooleanField(default=False)
    date = models.DateField(null=True)
    interval_min = models.PositiveIntegerField(default=0)
    interval_max = models.PositiveIntegerField(default=0)
    dows = DOWArrayField(default=[])

    user1 = models.ForeignKey(User, related_name='tempreport_user1_set')
    report1_creation_date = models.DateField(null=True)
    report1_mark = models.PositiveSmallIntegerField(null=True)
    report1_comment = models.TextField(null=True)

    user2 = models.ForeignKey(User, related_name='tempreport_user2_set')
    report2_creation_date = models.DateField(null=True)
    report2_mark = models.PositiveSmallIntegerField(null=True)
    report2_comment = models.TextField(null=True)

    creation_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    mail_sent = models.BooleanField(default=False)

    objects = TempReportManager()

    @property
    def opened(self):
        return self.is_opened()
        
    def is_opened(self):
        """Return True if actual date is between start and end date"""
        today = datetime.date.today()
        #return self.start_date <= today and self.end_date >= today
        return True

    def print_dows(self):
        """Displays Days Of Week"""
        return u'-'.join([value for (key, value) in Trip.DOWS
            if key in self.dows])
    
    def other_user(self, active_user):
        """Return the other user for this temp report"""
        if (self.user1 == active_user):
            return self.user2
        else:
            return self.user1
    
    def transform(self, both_reports=True):
        """Transform a temporary report (assessement) into a real report.
        Temporary report is destroyed
        """
        if both_reports and (not self.report1_mark or not self.report2_mark):
            # security
            return

        nb_reports_created = 0
        if self.report2_mark:
            report1 = Report(
                user=self.user1,
                from_user=self.user2,
                creation_date=self.report2_creation_date,
                mark=self.report2_mark,
                comment=self.report2_comment
            )
            report1.save()
            nb_reports_created += 1
        if self.report1_mark:
            report2 = Report(
                user=self.user2,
                from_user=self.user1,
                creation_date=self.report1_creation_date,
                mark=self.report1_mark,
                comment=self.report1_comment
            )
            report2.save()
            nb_reports_created += 1
        self.delete()
        return nb_reports_created

    def save(self):
        """Save the record. 
        
        Fill in the creation date, start_date and end_date fields, then call
        the parent save() method
        """
        if not self.id:
            self.creation_date = datetime.date.today()
            if self.regular:
                # creation_date + delay
                self.start_date = (self.creation_date +
                    datetime.timedelta(days=self.REGULAR_TRIP_DELAY))
            else:
                # date + interval_max + delay
                self.start_date = (self.date +
                    datetime.timedelta(days=self.interval_max) +
                    datetime.timedelta(days=self.PONCTUAL_TRIP_DELAY))
            self.end_date = (self.start_date +
                datetime.timedelta(days=self.CLOSE_DELAY))
        super(TempReport, self).save()
