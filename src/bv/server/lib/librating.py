# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
"""Provides a common way to interact with bisonvert serverside rating data 

"""
#python import
import datetime

#django import
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from django.utils.datastructures import SortedDict

#ecov import
from bv.server.rating.forms import ReportForm
from bv.server.rating.models import TempReport, Report
from bv.server.utils.paginator import PaginatorRender

# lib import
from bv.server.lib.exceptions import *

#__fixtures__ = ['accounts.json','lib_cities.json','lib_trips.json',]

class LibRating:    
    def _get_report_ordering(self):
        return {
            'date': ['creation_date'],
            '-date': ['-creation_date'],
            'user': ['auth_user2.username'],
            '-user': ['-auth_user2.username'],
            'mark': ['mark'],
            '-mark': ['-mark'],
            'comment': ['comment'],
            '-comment': ['-comment'],
        }
        
    def _get_tempreport_ordering(self):
        return {
            'departure': ['departure_city'],
            '-departure': ['-departure_city'],
            'arrival': ['arrival_city'],
            '-arrival': ['-arrival_city'],
            'date': ['dows', 'date'],
            '-date': ['-dows', '-date'],
            'type': ['type'],
            '-type': ['-type'],
            'user': ['user'],
            '-user': ['-user'],
            'write_date': ['start_date'],
            '-write_date': ['-start_date'],
        }
    
    def list_reports_for_user(self, user, ordered_by=None):
        """List all reports about a given user
        
        """
        ordered_by = ordered_by or 'date'
        oargs = self._get_report_ordering()[ordered_by]
        return Report.objects.select_related().filter(user=user).order_by(*oargs)
        
    
    def list_reports_from_user(self, user, ordered_by=None):
        """List all reports given by a given user.

        """
        ordered_by = ordered_by or 'date'
        oargs = self._get_report_ordering()[ordered_by]
        return Report.objects.select_related().filter(from_user=user).order_by(*oargs)

    def list_tempreports_for_user(self, user, ordered_by=None):
        """List temporary reports for a given user.
        
        Only tempreports that aren't marked anymore are returned, and only if 
        the specified user is a part of the tempreport user.
          
        """
        ordered_by = ordered_by or 'date'
        oargs = self._get_tempreport_ordering()[ordered_by]
        return TempReport.objects.get_user_tempreports(user).order_by(*oargs)


    def rate_user(self, user, tempreport_id, post_data):
        """Rate an user

        Rate the specified user.
        
        Check that logged user is one of the two registred in temporary report, 
        that the mak process is open, and that logged user havn't already give
        his mark.
        
        """
        tempreport = get_object_or_404(TempReport, pk=tempreport_id)
        if (tempreport.user1.id is not user.id
                and tempreport.user2.id is not user.id):
            raise InvalidUser()

        if not tempreport.is_opened():
            raise TempReportIsntOpen()

        if (tempreport.user1.id is user.id
                and tempreport.report1_mark is not None):
            raise MarkAlreadyExists()
            
        if (tempreport.user2.id is user.id
                and tempreport.report2_mark is not None):
            raise MarkAlreadyExists()
        
        form = ReportForm(post_data)
        if form.is_valid():
            if user.id is tempreport.user1.id:
                tempreport.report1_creation_date = datetime.date.today()
                tempreport.report1_mark = form.cleaned_data['mark']
                tempreport.report1_comment = form.cleaned_data['comment']
            else:
                tempreport.report2_creation_date = datetime.date.today()
                tempreport.report2_mark = form.cleaned_data['mark']
                tempreport.report2_comment = form.cleaned_data['comment']
            tempreport.save()
            if tempreport.report1_mark and tempreport.report2_mark:
                # both user are evaluated
                tempreport.transform()
        else:
            raise InvalidReportForm()
        
        return tempreport; 
