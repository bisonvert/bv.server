# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from django.utils.datastructures import SortedDict

from django.contrib.auth.decorators import login_required
from bv.server.rating.forms import ReportForm
from bv.server.rating.models import TempReport, Report
from bv.server.utils.paginator import PaginatorRender

import datetime

_RATING_PG = [5, 10, 20, 50]

@login_required
def my_reports(request):
    """Homepage for "my evaluation" section

    Redirect to my reports list
    """
    return list_tempreports(request, 1)

@login_required
def list_my_reports(request, page=1):
    """List all assessments given to active user
    
    Paginated list, with order sorting on columns
    """
    ordering = {
        'date': ['creation_date'],
        '-date': ['-creation_date'],
        'user': ['auth_user2.username'],
        '-user': ['-auth_user2.username'],
        'mark': ['mark'],
        '-mark': ['-mark'],
        'comment': ['comment'],
        '-comment': ['-comment'],
    }

    pgnum = _RATING_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _RATING_PG:
                pgnum = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pgnum
    get_url = '?pg=%d&order=%s' % (pgnum, order)

    oargs = ordering[order]

    paginator = PaginatorRender(
        Report.objects.select_related().filter(user=request.user)\
                .order_by(*oargs),
        page,
        pgnum,
        allow_empty_first_page=True,
        extra_context = {
            'current_item': 14,
            'current_nav_item': 1,
            'paginations': _RATING_PG,
            'order': order,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
        }
    )
    return paginator.render(request, 'rating/list_my_reports.html')

@login_required
def list_other_reports(request, page=1):
    """List all assessments by connected user.

    Paginated list, with order sorting on columns
    """
    ordering = {
        'date': ['creation_date'],
        '-date': ['-creation_date'],
        'user': ['auth_user.username'],
        '-user': ['-auth_user.username'],
        'mark': ['mark'],
        '-mark': ['-mark'],
        'comment': ['comment'],
        '-comment': ['-comment'],
    }

    pgnum = _RATING_PG[0]
    order = 'date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _RATING_PG:
                pgnum = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pgnum
    get_url = '?pg=%d&order=%s' % (pgnum, order)

    oargs = ordering[order]

    paginator = PaginatorRender(
        Report.objects.select_related().filter(from_user=request.user)\
                .order_by(*oargs),
        page,
        pgnum,
        allow_empty_first_page=True,
        extra_context = {
            'current_item': 14,
            'current_nav_item': 2,
            'paginations': _RATING_PG,
            'order': order,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
        }
    )
    return paginator.render(request, 'rating/list_other_reports.html')

@login_required
def list_tempreports(request, page=1):
    """Temporary assessments for connected user

    Paginated list, with order sorting on columns
    """
    ordering = {
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

    pgnum = _RATING_PG[0]
    order = 'write_date'
    if 'pg' in request.GET:
        try:
            if int(request.GET['pg']) in _RATING_PG:
                pgnum = int(request.GET['pg'])
        except ValueError:
            pass
    if 'order' in request.GET and request.GET['order'] in ordering:
        order = request.GET['order']
    get_url_pg = '?pg=%d' % pgnum
    get_url = '?pg=%d&order=%s' % (pgnum, order)

    oargs = ordering[order]
    
    tr = TempReport.objects.get_user_tempreports(request.user)
    tr = tr.select_related().order_by(*oargs)
        
    paginator = PaginatorRender(
        tr,
        page,
        pgnum,
        allow_empty_first_page=True,
        extra_context = {
            'current_item': 14,
            'current_nav_item': 3,
            'paginations': _RATING_PG,
            'order': order,
            'get_url_pg': get_url_pg,
            'get_url': get_url,
        }
    )
    return paginator.render(request, 'rating/list_tempreports.html')

@login_required
def rate_user(request, tempreport_id):
    """Rate an user

    Rate the user, then, if both carpoolers have rated the other one, redirect
    them to the temporary report list
    
    Check that logged user is one of the two registred in temporary report, 
    that the mak process is open, and that logged user havn't already give
    his mark.
    
    This view is accessible via GET or POST.

    GET displays the form
    POST get and process data.
    On errors, display again the form (via GET)

    This view is only accessible by connected users
    """
    tempreport = get_object_or_404(TempReport, pk=tempreport_id)
    if (tempreport.user1.id is not request.user.id
            and tempreport.user2.id is not request.user.id):
        raise Http404

    if not tempreport.is_opened():
        raise Http404

    if (tempreport.user1.id is request.user.id
            and tempreport.report1_mark is not None):
        raise Http404
    if (tempreport.user2.id is request.user.id
            and tempreport.report2_mark is not None):
        raise Http404

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            if request.user.id is tempreport.user1.id:
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
            return HttpResponseRedirect(reverse(
                'rating:list_temp_reports',args=[1]))
    else:
        form = ReportForm()
    response_dict = {
        'current_item': 14,
        'current_nav_item': 3,
        'form': form,
        'tempreport': tempreport,
    }

    template = loader.get_template('rating/rate_user.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))
