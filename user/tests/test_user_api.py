from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''Test the users API(public)'''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''Test creating a valid user'''
        payload = {
            'email': 'test123@xyz.com',
            'password': 'test@123',
            'name': 'testuser'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload.get('password')))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        '''Test creating a user that already exists'''
        payload = {
            'email': 'test123@xyz.com',
            'password': 'test@123',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_password_too_short(self):
        '''Test that password must be 5 characters long'''
        payload = {
            'email': 'test123@xyz.com',
            'password': 'tes',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        user_exists = get_user_model().objects.filter(
            email=payload.get('email')
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test that a token is created for a user'''
        payload = {
            'email': 'test123@xyz.com',
            'password': 'test@123',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(status.HTTP_200_OK, res.status_code)

    def test_create_token_invalid_credentials(self):
        '''Test no token creation if credentials invalid'''
        create_user(email='test123@xyz.com', password='test@123')
        payload = {
            'email': 'test123@xyz.com',
            'password': 'test@1235',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_create_token_user_not_exist(self):
        '''Test that token not created if user does not exist'''
        payload = {
            'email': 'test123@xyz.com',
            'password': 'test@1235',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_create_token_missing_field(self):
        '''Test that email and password are required'''
        payload = {
            'email': 'test123@xyz.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
