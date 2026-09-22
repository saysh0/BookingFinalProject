from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from listings.models import Listing

# Create your tests here.

User = get_user_model()


class ListingTest(TestCase):
    """Тесты объявлений / Listing tests."""

    def setUp(self):
        self.client = APIClient()
        landlord_group, _ = Group.objects.get_or_create(name='Landlord')
        tenant_group, _ = Group.objects.get_or_create(name='Tenant')

        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@test.com',
            password='testpass123'
        )
        self.landlord.groups.add(landlord_group)

        self.tenant = User.objects.create_user(
            username='tenant',
            email='tenant@test.com',
            password='testpass123'
        )
        self.tenant.groups.add(tenant_group)

        self.listing = Listing.objects.create(
            owner=self.landlord,
            title='Test Listing',
            location='Berlin, Hauptstraße 5',
            description='Test description',
            price=500,
            price_currency='EUR',
            rooms=2,
            housing_type='apartment',
            is_active=True
        )

    def test_list_listings_unauthenticated(self):
        """Просмотр объявлений без авторизации / View listings without auth."""
        response = self.client.get('/api/listings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_listing_as_landlord(self):
        """Создание объявления арендодателем / Create listing as landlord."""
        self.client.force_authenticate(user=self.landlord)
        response = self.client.post('/api/listings/', {
            'title': 'New Listing',
            'location': 'Munich, Marienplatz 1',
            'description': 'Nice place',
            'price': 800,
            'price_currency': 'EUR',
            'rooms': 3,
            'housing_type': 'apartment',
            'is_active': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_listing_as_tenant(self):
        """Создание объявления арендатором — запрещено / Create listing as tenant — forbidden."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/listings/', {
            'title': 'New Listing',
            'location': 'Munich, Marienplatz 1',
            'description': 'Nice place',
            'price': 800,
            'price_currency': 'EUR',
            'rooms': 3,
            'housing_type': 'apartment',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_price(self):
        """Фильтрация по цене / Filter by price."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.get('/api/listings/?price_min=100&price_max=600')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_listing_as_owner(self):
        """Удаление объявления владельцем / Delete listing as owner."""
        self.client.force_authenticate(user=self.landlord)
        response = self.client.delete(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_listing_as_other_user(self):
        """Удаление чужого объявления — запрещено / Delete other's listing — forbidden."""
        other_landlord = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        other_landlord.groups.add(Group.objects.get(name='Landlord'))
        self.client.force_authenticate(user=other_landlord)
        response = self.client.delete(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)