from django.test import TestCase, Client
from django.urls import reverse

from common.models import CustomUser
from feed.models import Source


class RegisterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'email': 'demo@gmail.com',
            'password': 'secret123',
            'first_name': 'demo',
            'cellphone': '09123456789',
            'last_name': 'user',
        }
        # CustomUser.objects.create_user(**self.credentials)

    def test_register(self):
        # print(reverse('register-user'))

        response = self.client.post(
            reverse('register-user'),
            self.credentials,
            content_type='application/json',
            follow=True
        )

        # print(response.__dict__)
        self.assertEqual(response.status_code, 204)
        user = CustomUser.get_with_email("demo@gmail.com")
        self.assertEqual(user.email, "demo@gmail.com")


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'email': 'demo@gmail.com',
            'password': 'secret123',
            'first_name': 'demo',
            'cellphone': '09123456789',
            'last_name': 'user',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }
        CustomUser.objects.create_user(**self.credentials)

    def test_login(self):
        # print(reverse('register-user'))

        response = self.client.post(
            reverse('login-user'),
            self.credentials,
            content_type='application/json',
            follow=True
        )

        # print(response.__dict__)
        self.assertEqual(response.status_code, 200)


