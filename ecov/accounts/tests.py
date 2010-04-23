# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.test import TestCase
from django.core import mail

class RegistrationTest(TestCase):
    fixtures = ['accounts.json']
    
    def setUp(self):
        self.urls = {
            'register': '/utilisateurs/inscription/',
            'confirm_registration': '/utilisateurs/confirmation_inscription/',
        }
    
    def test_view_exists(self):
        response = self.client.get(self.urls['register'])
        self.assertEquals(response.status_code, 200)

    def test_empty_registration(self):
        response = self.client.post(self.urls['register'], {})
        self.assertContains(response, 'This field is required.', count=4)

    def test_cgu_not_checked(self):
        response = self.client.post(self.urls['register'], {
            'email': 'not_a_real_email@email.com',
            'username': 'not_a_real_username',
            'password': 'anewpassword',
            'password2': 'anewpassword'
        })
        self.assertContains(response, 'You have to read and agree with the terms and conditions.')
        self.assertNotContains(response, 'This field is required.')

    def test_password_missmatch(self):
        response = self.client.post(self.urls['register'], {
            'email': 'not_a_real_email@email.com',
            'username': 'not_a_real_username',
            'password': 'anewpassword',
            'password2': 'anewpasswordxxxxxxx',
            'cgu': (1, )
        })
        self.assertContains(response, 'Password does not match.')
        self.assertNotContains(response, 'This field is required.')

    def test_password_too_short(self):
        response = self.client.post(self.urls['register'], {
            'email': 'not_a_real_email@email.com',
            'username': 'not_a_real_username',
            'password': 'pwd',
            'password2': 'pwd',
            'cgu': (1, )
        })
        self.assertNotContains(response, 'This field is required.')
        self.assertContains(response, 'Ensure this value has at least 6 characters (it has 3).', count=2)

    def test_valid_registering(self):
        response = self.client.post(self.urls['register'], {
            'email': 'not_a_real_email@email.com',
            'username': 'not_a_real_username',
            'password': 'anewpassword',
            'password2': 'anewpassword',
            'cgu': (1, )
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.urls['confirm_registration'])

        # check e-mail sent
        self.assertEquals(len(mail.outbox), 1, 'No mail sent when validating the user registration')
        self.assertEquals(mail.outbox[0].subject, 'BisonVert - Validation de votre adresse email')

