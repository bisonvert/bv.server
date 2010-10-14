# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.utils.translation import ugettext_lazy as _

from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django import forms

from bv.server.carpool import R_CITY_ZIP, str_slugify
from bv.server.carpool.models import FavoritePlace, Trip, City
from bv.server.carpool.forms import SearchTripForm
from bv.server.carpool.misc import get_date
from bv.server.carpool.forms import BaseForm
from bv.server.utils.fields import FRENCH_DATE_INPUT_FORMATS, FrenchDateField
from bv.server.utils.widgets import NullBooleanSelect, FrenchDateInput

import datetime
import time

#_DATES_CONCERT = (
#    (datetime.date(2008, 7, 7), '7/07/2008 - Nantes'),
#    (datetime.date(2008, 8, 7), '8/07/2008 - Nantes'),
#    (datetime.date(2008, 9, 7), '9/07/2008 - Nantes'),
#    (datetime.date(2008, 10, 7), '10/07/2008 - Nantes'),
#    (datetime.date(2008, 11, 7), '11/07/2008 - Nantes'),
#)

#_CITIES_CONCERT = [
#    City.objects.get(slug=u'nantes'),
#]

def get_dates_concert():
    today = datetime.date.today()
    return [date for date in _DATES_CONCERT if date[0] >= today]

class SearchTripRmll2009Form(BaseForm):
    departure_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure = forms.CharField(
        label=_("Departure:"),
        widget=forms.widgets.TextInput({'autocomplete': 'off'})
    )
    arrival = forms.CharField(
        label=_("Arrival:"),
        widget=forms.widgets.TextInput({'autocomplete': 'off'})
    )
    type = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    date = FrenchDateField(
        label=_("Date:"),
        required=False,
        initial=datetime.date.today(),
        widget=FrenchDateInput(attrs={
            'class':'type-date',
            'calendar_class':'calendarlink'
        })
    )

    def clean_departure(self):
        """Departure cleaner

        """
        return self.clean_route_point(base_name='departure')

    def clean_arrival(self):
        """Arrival cleaner

        """
        return self.clean_route_point(base_name='arrival')
        

def home(request):
    response_dict = {
        'current_item': 1,
        'gmapkey': settings.GOOGLE_MAPS_API_KEY,
        'places': FavoritePlace.objects.all().order_by('name'),
    }

    today = datetime.date.today()

    search_trip_details = request.session.get('search_trip_details', None)
    if search_trip_details:
        date = get_date(search_trip_details['date'], FRENCH_DATE_INPUT_FORMATS)
        if date < today:
            date = today
        data = {
            'departure': search_trip_details['departure']['name'],
            'departure_point': search_trip_details['departure']['point'],
            'departure_favoriteplace': search_trip_details['departure']['favoriteplace'] if 'favoriteplace' in search_trip_details['departure'] else None,
            'arrival': search_trip_details['arrival']['name'],
            'arrival_point': search_trip_details['arrival']['point'],
            'arrival_favoriteplace': search_trip_details['arrival']['favoriteplace'] if 'favoriteplace' in search_trip_details['arrival'] else None,
            'date': date,
            'type': Trip.OFFER
        }
    else:
        data = None
    
    dates_concert = get_dates_concert()

    if request.method == 'POST':
        if dates_concert:
            form = SearchTripRmll2009Form(request.POST)
        else:
            form = SearchTripForm(request.POST)
        if form.is_valid():
            try:
                trip_type = int(form.cleaned_data['type'])
            except:
                trip_type = Trip.OFFER
            search_trip_details = {
                'departure': {'name': form.cleaned_data['departure'], 'point': form.cleaned_data['departure_point'], 'favoriteplace': form.cleaned_data['departure_favoriteplace']},
                'arrival': {'name': form.cleaned_data['arrival'], 'point': form.cleaned_data['arrival_point'], 'favoriteplace': form.cleaned_data['arrival_favoriteplace']},
                'date': form.cleaned_data['date'].strftime("%d/%m/%Y") if form.cleaned_data['date'] else date_default.strftime("%d/%m/%Y")
            }
            request.session['search_trip_details'] = search_trip_details
            match_departure = R_CITY_ZIP.match(str_slugify(form.cleaned_data['departure']))
            match_arrival = R_CITY_ZIP.match(str_slugify(form.cleaned_data['arrival']))
            args = None
            if match_departure and match_arrival:
                args = [match_departure.group(1), match_departure.group(2), match_arrival.group(1), match_arrival.group(2)]

            if trip_type == Trip.OFFER:
                if args:
                    return HttpResponseRedirect(reverse('carpool:robots_search_offer_trip', args=args))
                else:
                    return HttpResponseRedirect(reverse('carpool:search_offer_trip'))
            else:
                if args:
                    return HttpResponseRedirect(reverse('carpool:robots_search_demand_trip', args=args))
                else:
                    return HttpResponseRedirect(reverse('carpool:search_demand_trip'))
    else:
        if dates_concert:
            form = SearchTripRmll2009Form(data)
        else:
            initial_data = {'date': today}
            form = SearchTripForm(data, initial=initial_data)
    response_dict.update({
        'form': form,
        'date_uptodate': dates_concert,
        'cities_concert': _CITIES_CONCERT,
    })

    template = loader.get_template('carpool/home_rmll2009.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))
