# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Forms for site module."""

from django.utils.translation import ugettext_lazy as _

from django import forms
from django.forms.models import ModelForm, model_to_dict
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException

from bv.server.carpool.models import CarType, Trip, TripOffer, TripDemand, City
from bv.server.utils.fields import FrenchDateField, FrenchDecimalField, SelectableTimeField
from bv.server.utils.widgets import FrenchDateInput, AutoCompleteTextInput, SelectableTimeWidget, NullBooleanSelect,CheckboxSelectMultipleAsArray

import datetime

# TODO: à supprimer quand les traductions django seront à jour
# pb de traduction: Assurez-vous que cette valeur fait moins de %(max)d
# caractères (il fait actuellement %(length)d caractères).
# il fait -> elle fait
_MAX_LENGTH = _(u'Ensure this value has at most %(max)d characters (it has '
        '%(length)d).')
_MIN_LENGTH = _(u'Ensure this value has at least %(min)d characters (it has '
        '%(length)d).')

SUBJECT_CHOICE = (
    ('', '---------'),
    (1, _("Report a bug")),
    (2, _("Suggestions")),
    (3, _("Comments")),
    (4, _("Encouragements")),
    (5, _("Other")),
)

ADDRESSTYPE_CHOICE = (
    (Trip.FROM, _("Come from")),
    (Trip.TO, _("Go to")),
)

DEPARTARRIVAL_CHOICE = (
    (Trip.FROM, _("Depart from city")),
    (Trip.TO, _("Arrival to city")),
)

class BaseForm(forms.Form):
    """Base form for the carpool app"""
    
    def get_point(self, geom_wkt):
        """Return a geometry of type "point" from a WKT point"""
        try:
            geometry = GEOSGeometry(geom_wkt)
            if geometry is None or geometry.geom_type != 'Point':
                return None
            return geometry
        except (ValueError, GEOSException):
            return None
        
    def clean_route_point(self, point_name = None, 
            point_alternate_name = None, displayable_name = None, base_name = None):
        """Route point (departure/arrival) cleaner for forms
        
        Check that the WKT traject point is well filled, and match to a 
        geometry of type point.
        
        """
        if base_name:
            if not point_name:
                point_name = base_name + "_point"

            if not point_alternate_name:
                point_alternate_name = base_name
            
            if not displayable_name:
                displayable_name = base_name.capitalize()
        
        if (point_name in self.cleaned_data and self.cleaned_data[point_name]):
            point = self.get_point(self.cleaned_data[point_name])
            if point:
                return self.cleaned_data[point_alternate_name]
        raise forms.ValidationError(_(displayable_name+" address not found."))

class SearchTripForm(BaseForm):
    """Form to find a trip announce.
    
    Contains:

    + departure city
    + arrival city
    + start date

    Hidden fields are:
    
    + point for departure city (by geocoding)
    + point for arrival city (by geocoding)
    + id of the favorite departure point
    + id of the favorite arrival point
    + search type: driver or passenger
    
    """
    departure_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure = forms.CharField(
        label=_("Departure:"),
        widget=AutoCompleteTextInput({'autocomplete': 'off'})
    )
    arrival_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival = forms.CharField(
        label=_("Arrival:"),
        widget=AutoCompleteTextInput({'autocomplete': 'off'})
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
        """Departure cleaner"""
        return self.clean_route_point(base_name = 'departure')

    def clean_arrival(self):
        """Arrival cleaner"""
        return self.clean_route_point(base_name = 'arrival')

class SearchTripSimpleForm(BaseForm):
    """Simplified search form.
    
    Contains:

    + a choice "Go from" or "Go to"
    + a city: (departure or arrival)

    Hidden fields are

    + the city point, by geocoding
    + the search type (driver or passenger)

    """
    address_type = forms.ChoiceField(
        label="",
        choices=ADDRESSTYPE_CHOICE,
    )
    point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    address = forms.CharField(
        label="",
        widget=forms.widgets.TextInput()
    )
    type = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )

    def clean_address(self):
        """Address cleaner"""
        return self.clean_route_point(point_name='point', 
                point_alternate_name='address', displayable_name='')
        
class SearchTripWithDatesForm(BaseForm):
    """Form to search a trip announce

    Contains:

    + departure city
    + arrival city
    + departure date (select)
    
    Hidden fields:

    + point of departure city (by geocoding in the client side)
    + point of arrival city (by geocoding in the client side)
    + favorite departure id
    + favorite arrival id
    + search type (driver or passenger)

    """
    departure_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    departure = forms.CharField(
        label=_("Departure:"),
        widget=forms.widgets.TextInput({'autocomplete': 'off'})
    )
    arrival_point = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival_favoriteplace = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    arrival = forms.CharField(
        label=_("Arrival:"),
        widget=forms.widgets.TextInput({'autocomplete': 'off'})
    )
    type = forms.IntegerField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    date = FrenchDateField()

    def __init__(self, dates, *args, **kwargs):
        super(SearchTripWithDatesForm, self).__init__(*args, **kwargs)
        self.fields['date'] = FrenchDateField(
            label=_("Date:"),
            required=False,
            widget=forms.widgets.Select(choices=dates),
        )

    def clean_departure(self):
        """Departure cleaner"""
        return self.clean_route_point(base_name = 'departure')

    def clean_arrival(self):
        """Arrival cleaner"""
        return self.clean_route_point(base_name = 'arrival')

class ChooseDepartArrivalCityForm(forms.Form):
    """Form to choose a departure or an arrival city

    Contains:

    + A choice "going to", or "going from"
    + a city

    For cities, javascript force a city choice by autocompletion

    """
    depart_arrival = forms.ChoiceField(
        label=_(u"Trips:"),
        choices=DEPARTARRIVAL_CHOICE,
    )
    city = forms.CharField(
        label=_(u"City:"),
        widget=AutoCompleteTextInput({'autocomplete': 'off', 'size': 40})
    )

    def __init__(self, *args, **kwargs):
        """Initialise the city object."""
        self.city_obj = None
        super(ChooseDepartArrivalCityForm, self).__init__(*args, **kwargs)

    def clean_city(self):
        """City cleaner.
        
        Check that entered city match with the city regexp
        
        Fetch the associated City object

        """
        self.city_obj = City.get_city(self.cleaned_data['city'])
        if self.city_obj:
            return self.cleaned_data['city']
        raise forms.ValidationError(_("Incorrect city."))

class EditTripForm(ModelForm):
    def __init__(self, instance=None, *args, **kwargs):
        super(EditTripForm, self).__init__(instance=instance, *args, **kwargs)
        if instance:
            if instance.offer and instance.demand:
                trip_type_value = Trip.BOTH
            elif instance.offer:
                trip_type_value = Trip.OFFER
            elif instance.demand:
                trip_type_value = Trip.DEMAND
            else:
                trip_type_value = Trip.BOTH
                                
            self.fields['trip_type'].initial = trip_type_value
        
    trip_type = forms.ChoiceField(
        label=_("Route type"),
        required=True,
        choices=((Trip.DEMAND, _("Demand")),(Trip.OFFER, _("Offer")),(Trip.BOTH, _("Both"))),
    )
    name = forms.CharField(
        label=_("Announce name:"),
        required=True,
        max_length=200,
    )
    departure_city = forms.CharField(
        label=_("Departure city:"),
        required=True,
        max_length=200,
    )
    departure_address = forms.CharField(
        label=_("Departure address:"),
        required=False,
        max_length=200,
    )
    arrival_city = forms.CharField(
        label=_("Arrival city:"),
        required=True,
        max_length=200,
    )
    arrival_address = forms.CharField(
        label=_("Arrival address:"),
        required=False,
        max_length=200,
    )
    comment = forms.CharField(
        label=_("Comment:"),
        max_length=300,
        required=False,
        widget=forms.widgets.Textarea(),
    )
    alert = forms.BooleanField(
        label=_("Email alert:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'}),
    )
    # date params
    regular = forms.BooleanField(
        widget=forms.widgets.Select(choices=((False, _("Punctual")),(True, _("Regular")))),
        label=_("Trip frequency"),
        required=False,
    )
    date = FrenchDateField(
        label=_("Date"),
        required=False,
    )
    interval_min = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=0,
    )
    interval_max = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=0,
    )
    time = SelectableTimeField(
        label=_("Departure at about"),
        required=False,
        widget=SelectableTimeWidget
    )
    departure_point = forms.CharField(
        widget=forms.widgets.HiddenInput()
    )
    arrival_point = forms.CharField(
        widget=forms.widgets.HiddenInput()
    )
    dows = forms.MultipleChoiceField(
        widget=CheckboxSelectMultipleAsArray,
        required=False,
        choices=((0,_('Mon')),(1,_('Tue')), (2,_('Wed')), (3,_('Thu')), (4,_('Fri')), (5,_('Sat')), (6,_('Sun'))),
    )
    
    class Meta:
        """Meta class.
        
        Define used model fields

        """
        model = Trip
        fields = (
            'name', 
            'departure_city', 
            'departure_address', 
            'departure_point', 
            'arrival_city', 
            'arrival_address',
            'arrival_point',
            'date', 
            'interval_min', 
            'interval_max', 
            'time', 
            'comment', 
            'alert',
            'dows',
            'regular',
        )
    
class EditTripOfferOptionsForm(ModelForm):

    driver_km_price = FrenchDecimalField(
        label=_("Asking price by kilometer:"),
        max_digits=7,
        decimal_places=2,
        required=False,
    )
    driver_smokers_accepted = forms.NullBooleanField(
        label=_("Smokers accepted:"),
        required=False,
        widget=NullBooleanSelect,
    )
    driver_pets_accepted = forms.NullBooleanField(
        label=_("Pets accepted:"),
        required=False,
        widget=NullBooleanSelect,
    )
    driver_place_for_luggage = forms.NullBooleanField(
        label=_("Place for luggages:"),
        required=False,
        widget=NullBooleanSelect,
    )
    driver_car_type = forms.ModelChoiceField(
        label=_("Car type:"),
        required=False,
        queryset=CarType.objects.all(),
    )
    driver_seats_available = forms.IntegerField(
        label=_("Seat number by default:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '5'})
    )
    route = forms.CharField(
        widget=forms.widgets.HiddenInput()
    )
    steps = forms.CharField(
        widget=forms.widgets.HiddenInput()
    )
    radius = forms.IntegerField(
        initial=500,
        widget=forms.widgets.HiddenInput()
    )
    
    class Meta:
        """Meta class.
        
        Define used model fields

        """
        model = TripOffer
        fields = (
            'driver_km_price', 
            'driver_smokers_accepted', 
            'driver_pets_accepted', 
            'driver_place_for_luggage', 
            'driver_car_type', 
            'driver_seats_available',
            'route',
            'radius',
            'steps',
        )
    
class EditTripDemandOptionsForm(ModelForm):
    passenger_max_km_price = FrenchDecimalField(
        label=_("Maximum price by kilometer:"),
        max_digits=7,
        decimal_places=2,
        required=False
    )
    passenger_smokers_accepted = forms.BooleanField(
        label=_("Smokers accepted first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_pets_accepted = forms.BooleanField(
        label=_("Pets accepted first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_place_for_luggage = forms.BooleanField(
        label=_("Place for luggages first:"),
        required=False,
        widget=forms.widgets.CheckboxInput({'class': 'checkbox'})
    )
    passenger_car_type = forms.ModelChoiceField(
        label=_("Car type first:"),
        required=False,
        queryset=CarType.objects.all(),
    )
    passenger_min_remaining_seats = forms.IntegerField(
        label=_("Minimum remaining seats:"),
        required=False,
        widget=forms.widgets.TextInput({'size': '5'})
    )
    radius = forms.IntegerField(
        initial=500,
        widget=forms.widgets.HiddenInput()
    )
    
    class Meta:
        """Meta class.
        
        Define used model fields

        """
        model = TripDemand
        fields = (
            'passenger_max_km_price', 
            'passenger_smokers_accepted', 
            'passenger_pets_accepted', 
            'passenger_place_for_luggage', 
            'passenger_car_type', 
            'passenger_min_remaining_seats',
            'radius',
        )

class AnonymousContactForm(forms.Form):
    """Anonymous contact form.

    Contains:

    + user name
    + user email
    + subject
    + title
    + message

    """
    name = forms.CharField(
        label=_("* Firstname / Lastname:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    email = forms.EmailField(
        label=_("* Email:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    subject = forms.ChoiceField(
        label=_("* Subject:"),
        choices=SUBJECT_CHOICE,
    )
    title = forms.CharField(
        label=_("* Title:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    message = forms.CharField(
        label=_("* Message:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )

class ContactForm(forms.Form):
    """Contact form for logged users

    Contains:

    + subject
    + title
    + message

    """
    subject = forms.ChoiceField(
        label=_("* Subject:"),
        choices=SUBJECT_CHOICE,
    )
    title = forms.CharField(
        label=_("* Title:"),
        widget=forms.widgets.TextInput({'size': '40'})
    )
    message = forms.CharField(
        label=_("* Message:"),
        widget=forms.widgets.Textarea({'rows': '12', 'cols': '60'})
    )
