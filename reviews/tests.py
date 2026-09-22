from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from listings.models import Listing
from bookings.models import Booking
from reviews.models import Review
import datetime

# Create your tests here.

User = get_user_model()


class ReviewTest(TestCase):
    """Тесты отзывов / Review tests."""

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

        # Завершённое бронирование / Completed booking
        self.completed_booking = Booking.objects.create(
            tenant=self.tenant,
            listing=self.listing,
            date_from=datetime.date.today() - datetime.timedelta(days=10),
            date_to=datetime.date.today() - datetime.timedelta(days=5),
            status=Booking.BookingStatus.APPROVED
        )

    def test_create_review_with_completed_booking(self):
        """Создание отзыва с завершённым бронированием / Create review with completed booking."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/reviews/', {
            'listing_id': self.listing.id,
            'rating': 5,
            'text': 'Great place!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_review_without_booking(self):
        """Нельзя оставить отзыв без бронирования / Cannot review without booking."""
        other_tenant = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        other_tenant.groups.add(Group.objects.get(name='Tenant'))
        self.client.force_authenticate(user=other_tenant)
        response = self.client.post('/api/reviews/', {
            'listing_id': self.listing.id,
            'rating': 5,
            'text': 'Great place!'
        })
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_cannot_review_twice(self):
        """Нельзя оставить два отзыва / Cannot review twice."""
        Review.objects.create(
            author=self.tenant,
            listing=self.listing,
            rating=4,
            text='Good place'
        )
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/reviews/', {
            'listing_id': self.listing.id,
            'rating': 5,
            'text': 'Great place!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews(self):
        """Просмотр списка отзывов / View review list."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)