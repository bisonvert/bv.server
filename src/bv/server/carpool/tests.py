# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from test.decorators import log_user
import re

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from bv.server.carpool.views import *
from bv.server.carpool.models import Trip

class CarpoolTestCase(TestCase):
    fixtures = ['accounts']

    def login(self):
        """Log the "test" user.

        """
        self.assertNotEqual(False, self.client.login(
            username='test', password='testtest'),
            '"test" user failed to login'
        )
        
class TripCreationTest(CarpoolTestCase):
    def setUp(self):
        """Before each test, reinitialize some data:
            + urls
            + data to send for add_modify_trip view
        """
        self.urls = {
            'add_trip': '/nouvelle_annonce/',
            'trip_results' : '/resultats_annonce/',
            'add_return_trip': '/annonce_retour/',

        }
        self.add_modify_trip_data = {
            'comment': '',
            'offer-radius': '500',
            'offer-driver_smokers_accepted': '1',
            'arrival_point': 'POINT(2.3965788 47.08289200000001)',
            'interval_max': '0',
            'date': '16/12/2009',
            'offer-steps': '[]',
            'trip_type': '0',
            'interval_min': '7',
            'demand-radius': '500',
            'return_trip': 'false',
            'departure_point': 'POINT(1.9039759 47.901386599999995)',
            'offer-driver_pets_accepted': '2',
            'arrival_address': '',
            'regular': 'False',
            'departure_city': 'bourges',
            'offer-driver_car_type': '',
            'alert': 'on',
            'departure_address': '',
            'offer-driver_seats_available': '',
            'name': 'test2',
            'offer-driver_place_for_luggage': '1',
            'offer-driver_km_price': '20.00',
            'time': '3',
            'offer-route': 'MULTILINESTRING((0 0, 1 1))',
            'arrival_city': 'orleans'
        }
        
    @log_user
    def test_add_modify_trip_empty_form(self):
        """Send the form without any data, and check that correct errors are 
        thrown.
        
        """
        response = self.client.post(self.urls['add_trip'], {})
        
        self.assertContains(response, 'This field is required.', count=8)
        
    @log_user
    def test_add_modify_trip_invalid_field(self):
        """Check that when requesting the view with invalid data, all data 
        remains, plus an error message.
        
        """
        self.add_modify_trip_data['offer-driver_km_price'] = '20.00 centimes'
        response = self.client.post(self.urls['add_trip'],self.add_modify_trip_data)
        self.assertContains(response, 'Enter a number.',1)  
        
        # for each given POST data values, checkified auth login view.
        for val in self.add_modify_trip_data:
            self.assertContains(response, self.add_modify_trip_data[val])
            
    @log_user
    def test_add_modify_trip_valid_data(self):
        """Check that, when requesting the view with valid data, the data is 
        inserted the right way.
        
        """
        response = self.client.post(self.urls['add_trip'], self.add_modify_trip_data, follow=True)
        redirection = response.redirect_chain[0][0]
        self.assertEquals(1, redirection.count(self.urls['trip_results']))
        identifier = re.compile('http://testserver/resultats_annonce/(?P<id>[0-9]*)/').sub(r'\g<id>', redirection)
        try:
            Trip.objects.get(id=identifier)
        except ObjectDoesNotExist:
            self.assertFalse(msg='the created trip doesnt exists')
            
    @log_user
    def test_add_modify_trip_with_return(self):
        """Creates a trip, and check that the traject has been created, and that
        the redirection works properly.
        
        """
        self.add_modify_trip_data['return_trip'] = 'true'
        response = self.client.post(self.urls['add_trip'], self.add_modify_trip_data, follow=True)
        redirection = response.redirect_chain[0][0]
        self.assertEquals(1, redirection.count(self.urls['add_return_trip']))
        identifier = re.compile('http://testserver/annonce_retour/(?P<id>[0-9]*)/').sub(r'\g<id>', redirection)
        try:
            Trip.objects.get(id=identifier)
        except ObjectDoesNotExist:
            self.assertFalse(msg='the created trip doesnt exists')

class AjaxTripResultsTest(CarpoolTestCase):
    def SetUp(self):
        self.urls = {
            'ajax_get_trips': 'ajax/get_trips/',
            'ajax_get_trips_results': 'ajax/get_trips/',
        }
    
    def test_view(self):
        pass
    
    def test_unexisting_trip(self):
        """when requesting results for an unexisting trip, return a 404 error
        
        """
        pass

    def text_existing_trip(self):
        pass
