from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    '''Test cases for models'''

    def test_create_user_with_email_successfully(self):
        '''Test creating a new user with email successfully'''
        email = 'test123@xyz.com'
        password = 'abc@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_with_email_normalized(self):
        '''Test new user with normalized email'''
        email = 'test123@XYZ.COM'
        password = 'abc@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_with_valid_email(self):
        '''Test creating a new user with valid email'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'abc@123')

    def test_create_superuser(self):
        '''Test creating a superuser'''
        superuser = get_user_model().objects.create_superuser(
            email='test123@xyz.com',
            password='abc@123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
