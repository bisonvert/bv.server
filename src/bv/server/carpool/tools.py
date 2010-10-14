# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Webmaster tools"""

from django.utils.translation import ugettext_lazy as _

from django import forms
from django.template import RequestContext, loader
from django.http import HttpResponse, Http404

from django.conf import settings

from bv.server.carpool.forms import ChooseDepartArrivalCityForm
from bv.server.carpool.models import Trip, City
from bv.server.carpool.misc import get_date, FRENCH_DATE_INPUT_FORMATS
from bv.server.carpool.views import home
from utils.fields import FrenchDateField
from utils.widgets import AutoCompleteTextInput, FrenchDateInput

IFRAME_FORMATS = {
    '490x90': {
        'name': '490px x 90px', 'width': 490, 'height': 90,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
    '500x200': {
        'name': '500px x 200px', 'width': 500, 'height': 200,
        'autocomplete': True, 'favorite_places': False,
        'with_date': True, 'trip_list': True,
    },
    '800x130': {
        'name': '800px x 130px', 'width': 800, 'height': 130,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
    '200x170': {
        'name': '200px x 170px', 'width': 200, 'height': 170,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
    '240x240': {
        'name': '240px x 240px', 'width': 240, 'height': 240,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
    '250x400': {
        'name': '250px x 400px', 'width': 250, 'height': 400,
        'autocomplete': True, 'favorite_places': True,
        'with_date': True, 'trip_list': False,
    },
    '150x200': {
        'name': '150px x 200px', 'width': 150, 'height': 200,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
    '135x200': {
        'name': '135px x 200px', 'width': 135, 'height': 200,
        'autocomplete': False, 'favorite_places': False,
        'with_date': False, 'trip_list': False,
    },
}
IFRAME_FORMATS_KEYS = IFRAME_FORMATS.keys()
IFRAME_FORMATS_KEYS.sort()
IFRAME_THEMES = {
    'normal': {
        'name': 'Thème %s' % settings.PROJECT_NAME
    },
    'ffe': {
        'name': _('FFE theme'),
    },
    'rmll': {
        'name':  _('RMLL theme'),
    },
    'flowers': {
        'name':  _('flower theme'),
    },
    'sky': {
        'name':  _('Sky theme'),
    },
    'south': {
        'name':  _('South theme'),
    },
    'grey': {
        'name':  _('Grey theme'),
    },
    'rmll2009': {
        'name': _('RMLL 2009 theme'),
    },
}
IFRAME_THEMES_KEYS = IFRAME_THEMES.keys()
IFRAME_THEMES_KEYS.sort()

class IFrameFormChooserForm(forms.Form):
    """Form to choose an Iframe of type form"""
    format = forms.ChoiceField(
        label=_("Format:"),
        choices=[(item, IFRAME_FORMATS[item]['name'])
                for item in IFRAME_FORMATS_KEYS],
    )
    theme = forms.ChoiceField(
        label=_("Theme:"),
        choices=[(item, IFRAME_THEMES[item]['name'])
                for item in IFRAME_THEMES_KEYS],
    )
    date = FrenchDateField(
        label=_("Date:"),
        required=False,
        widget=FrenchDateInput(attrs={
            'class':'type-date',
            'calendar_class':'calendarlink'
        })
    )
    departure = forms.CharField(
        label=_(u"Departure city:"),
        required=False,
        widget=AutoCompleteTextInput({'autocomplete': 'off', 'size': 40})
    )
    arrival = forms.CharField(
        label=_(u"Arrival city:"),
        required=False,
        widget=AutoCompleteTextInput({'autocomplete': 'off', 'size': 40})
    )

    def __init__(self, *args, **kwargs):
        super(IFrameFormChooserForm, self).__init__(*args, **kwargs)
        self.departure_obj = None
        self.arrival_obj = None

    def clean_departure(self):
        """Departure city cleaner
        
        Checks that the city match with the city displaying regexp.
        
        Fetch the associated city object

        """
        self.departure_obj = City.get_city(self.cleaned_data['departure'])
        if not self.departure_obj and self.cleaned_data['departure']:
            raise forms.ValidationError(_("Incorrect city."))
        return self.cleaned_data['departure']

    def clean_arrival(self):
        """Arrival city cleaner

        Checks that the city match with the city displaying regexp.
        
        Fetch the associated city object

        Fetche l'objet City associé.

        """
        self.arrival_obj = City.get_city(self.cleaned_data['arrival'])
        if not self.arrival_obj and self.cleaned_data['arrival']:
            raise forms.ValidationError(_("Incorrect city."))
        return self.cleaned_data['arrival']

class IFrameListChooserForm(ChooseDepartArrivalCityForm):
    """form to choose an Iframe of type "list" """
    MIN = 300
    MIN_TRIPS = 5
    MAX_TRIPS = 100
    width = forms.IntegerField(
        label=_("Iframe's width:"),
        min_value=MIN,
        help_text=_("minimum %(num)dpx") % {'num': MIN},
        initial=600,
    )
    height = forms.IntegerField(
        label=_("Iframe's height:"),
        min_value=MIN,
        help_text=_("minimum %(num)dpx") % {'num': MIN},
        initial=400,
    )
    trip_num = forms.IntegerField(
        label=_("Displayed trip number:"),
        min_value=MIN_TRIPS,
        max_value=MAX_TRIPS,
        help_text=_("minimum %(min)d, maximum %(max)d" % {
            'min': MIN_TRIPS,
            'max': MAX_TRIPS
        }),
        initial=15,
    )

def choose_iframe_form(request):
    """Vue pour choisir une iframe de type formulaire.

    Le formulaire permet de choisir un thème et un format.

    Vue accessible en GET ou en POST:

    + GET: affichage d'un formulaire.
    + POST: récupération des données postées, traitement des données.
      + en cas d'erreur, réaffichage du formulaire.
      + si aucune erreur n'est levée, réaffichage du formulaire, et affichage
        du code de l'iframe qui correspond, avec un aperçu.

    """
    valid = False
    format_id = None
    format_dict = None
    theme_id = None
    theme_dict = None
    if request.method == 'POST':
        form = IFrameFormChooserForm(request.POST)
        if form.is_valid():
            format_id = form.cleaned_data['format']
            format_dict = IFRAME_FORMATS[format_id]
            theme_id = form.cleaned_data['theme']
            theme_dict = IFRAME_THEMES[theme_id]
            valid = True
    else:
        form = IFrameFormChooserForm()

    response_dict = {
        'current_footer_item': 4,
        'form': form,
        'valid': valid,
        'format_id': format_id,
        'format_dict': format_dict,
        'theme_id': theme_id,
        'theme_dict': theme_dict,
    }

    template = loader.get_template('carpool/tools/choose_iframe_form.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def iframe_form(request, theme, format, date=None, departure_slug=None,
        departure_zip=None, arrival_slug=None, arrival_zip=None):
    """Display the content of the Ifram of type "form"/
    
    Checks that the theme and the format matches.
    
    Simple form: departuire, arrival, date (if there is place to display it),
    2 buttons (seeking for conductor or for passenger)

    """
    if theme not in IFRAME_THEMES:
        raise Http404
    if format not in IFRAME_FORMATS:
        raise Http404
    # get date and cities
    departure, arrival = None, None
    if date != '00-00-0000':
        date = get_date(date, FRENCH_DATE_INPUT_FORMATS)
    else:
        date = None
    if departure_slug:
        try:
            departure = City.objects.get_from_slug(departure_slug,
                    int(departure_zip))
        except City.DoesNotExist:
            departure = None
    if arrival_slug:
        try:
            arrival = City.objects.get_from_slug(arrival_slug, int(arrival_zip))
        except City.DoesNotExist:
            arrival = None
    return home(request, layout='iframe', theme_id=theme,
            theme_dict=IFRAME_THEMES[theme], format_id=format,
            format_dict=IFRAME_FORMATS[format], date=date, departure=departure,
            arrival=arrival)

def home_rmll2008(request):
    """special view for RMLL 2008"""
    return home(request, layout='rmll2008')

def choose_iframe_list(request):
    """Choose an Iframe of type "list".
    
    The form allows us to choose a departure or an arrival city, the iframe 
    size, and the number of possible announces.
    
    this view is accessible via GET and POST.
    
    GET display the form and POST manage and deals with data.
    
    If an error occurs, display again the form.

    """
    valid = False
    is_depart = False
    city, width, height, trip_num = None, None, None, None
    if request.method == 'POST':
        form = IFrameListChooserForm(request.POST)
        if form.is_valid():
            if int(form.cleaned_data['depart_arrival']) == Trip.FROM:
                is_depart = True
            city = form.city_obj
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            trip_num = form.cleaned_data['trip_num']
            valid = True
    else:
        form = IFrameListChooserForm()

    response_dict = {
        'current_footer_item': 4,
        'form': form,
        'valid': valid,
        'is_depart': is_depart,
        'city': city,
        'width': width,
        'height': height,
        'trip_num': trip_num,
    }

    template = loader.get_template('carpool/tools/choose_iframe_list.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def iframe_list(request, city_slug, city_zip, trip_num, is_depart):
    """Generic view for iframe list
    
    check that the parameter trip_num is between the defined borns.
    
    Displays the N last announces (sorted by modification date) from or to a 
    city, in a radius of 10km.

    """
    # get city
    try:
        city = City.objects.get_from_slug(city_slug, int(city_zip))
    except City.DoesNotExist:
        raise Http404
    # check trip_num
    if (int(trip_num) < IFrameListChooserForm.MIN_TRIPS
            or int(trip_num) > IFrameListChooserForm.MAX_TRIPS):
        trip_num = IFrameListChooserForm.MIN_TRIPS
    # radius
    radius = 10000
    # queryset
    if is_depart:
        trips = Trip.objects.get_trip_from_city(
                city.point, radius
        ).exclude_outdated().order_by('-modification_date')[:trip_num]
    else:
        trips = Trip.objects.get_trip_to_city(
                city.point, radius
        ).exclude_outdated().order_by('-modification_date')[:trip_num]

    response_dict = {
        'trips': trips,
        'city': city,
        'is_depart': is_depart,
    }

    template = loader.get_template('carpool/tools/iframe_list.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

def iframe_list_depart_from(request, departure_slug, departure_zip, trip_num):
    """Displays the iframe content of a "list" type, departing from a city.

    """
    return iframe_list(request, departure_slug, departure_zip, trip_num, True)

def iframe_list_arrival_to(request, arrival_slug, arrival_zip, trip_num):
    """Displays the iframe content for a "list" type, bound to a city

    """
    return iframe_list(request, arrival_slug, arrival_zip, trip_num, False)

def choose_banner(request):
    """TODO: direct_to_template"""
    response_dict = {
        'current_footer_item': 4,
    }

    template = loader.get_template('carpool/tools/choose_banner.html')
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))

