from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_retrieve_user_unauthorized(self):
        '''Test that authentication is required for users'''
        res = self.client.get(ME_URL)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class PrivateUserApiTests(TestCase):
    '''Test API requests that require authentication'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test123@xyz.com',
            password='test@123',
            name='testuser'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        '''Test retrieving user profile for logged in user'''
        res = self.client.get(ME_URL)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual({
            'name': self.user.name,
            'email': self.user.email
        }, res.data)

    def test_post_me_not_allowed(self):
        '''Test that POST is not allowed on me url'''
        res = self.client.post(ME_URL, {})

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, res.status_code)

    def test_update_user_profile(self):
        '''Test updating the user profile for authenticated user'''
        payload = {
            'name': 'new name',
            'password': 'test@321'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload.get('name'))
        self.assertTrue(self.user.check_password(payload.get('password')))
        self.assertEqual(status.HTTP_200_OK, res.status_code)
