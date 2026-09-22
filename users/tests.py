from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

# Create your tests here.

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователей / User registration tests."""

    def setUp(self):
        self.client = APIClient()
        Group.objects.get_or_create(name='Landlord')
        Group.objects.get_or_create(name='Tenant')

    def test_register_landlord(self):
        """Регистрация арендодателя / Landlord registration."""
        response = self.client.post('/api/users/', {
            'username': 'landlord',
            'email': 'landlord@test.com',
            'password': 'testpass123',
            'groups': ['Landlord']
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='landlord@test.com')
        self.assertTrue(user.groups.filter(name='Landlord').exists())

    def test_register_tenant(self):
        """Регистрация арендатора / Tenant registration."""
        response = self.client.post('/api/users/', {
            'username': 'tenant',
            'email': 'tenant@test.com',
            'password': 'testpass123',
            'groups': ['Tenant']
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='tenant@test.com')
        self.assertTrue(user.groups.filter(name='Tenant').exists())

    def test_register_duplicate_email(self):
        """Регистрация с дублирующимся email / Registration with duplicate email."""
        User.objects.create_user(username='existing', email='existing@test.com', password='test123')
        response = self.client.post('/api/users/', {
            'username': 'new',
            'email': 'existing@test.com',
            'password': 'testpass123',
            'groups': ['Tenant']
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_group(self):
        """Регистрация с неверной группой / Registration with invalid group."""
        response = self.client.post('/api/users/', {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'testpass123',
            'groups': ['InvalidGroup']
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(TestCase):
    """Тесты входа пользователей / User login tests."""

    def setUp(self):
        self.client = APIClient()
        Group.objects.get_or_create(name='Tenant')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_login_with_email(self):
        """Вход по email / Login with email."""
        response = self.client.post('/api/token/', {
            'email': 'test@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """Вход с неверным паролем / Login with wrong password."""
        response = self.client.post('/api/token/', {
            'email': 'test@test.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated(self):
        """Просмотр профиля авторизованным пользователем / View profile as authenticated user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@test.com')

    def test_profile_unauthenticated(self):
        """Просмотр профиля неавторизованным пользователем / View profile as unauthenticated user."""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
