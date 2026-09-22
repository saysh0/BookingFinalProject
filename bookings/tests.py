from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from listings.models import Listing
from bookings.models import Booking
import datetime

# Create your tests here.

User = get_user_model()


class BookingTest(TestCase):
    """Тесты бронирований / Booking tests."""

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

        self.booking = Booking.objects.create(
            tenant=self.tenant,
            listing=self.listing,
            date_from=datetime.date.today() + datetime.timedelta(days=5),
            date_to=datetime.date.today() + datetime.timedelta(days=10),
            status=Booking.BookingStatus.IN_PROGRESS
        )

    def test_create_booking_as_tenant(self):
        """Создание бронирования арендатором / Create booking as tenant."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/bookings/', {
            'listing_id': self.listing.id,
            'date_from': str(datetime.date.today() + datetime.timedelta(days=15)),
            'date_to': str(datetime.date.today() + datetime.timedelta(days=20)),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_book_own_listing(self):
        """Арендодатель не может забронировать своё объявление / Landlord cannot book own listing."""
        self.client.force_authenticate(user=self.landlord)
        response = self.client.post('/api/bookings/', {
            'listing_id': self.listing.id,
            'date_from': str(datetime.date.today() + datetime.timedelta(days=15)),
            'date_to': str(datetime.date.today() + datetime.timedelta(days=20)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_past_dates(self):
        """Нельзя бронировать прошедшие даты / Cannot book past dates."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/bookings/', {
            'listing_id': self.listing.id,
            'date_from': str(datetime.date.today() - datetime.timedelta(days=5)),
            'date_to': str(datetime.date.today() - datetime.timedelta(days=1)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlapping_dates(self):
        """Пересечение дат / Overlapping dates."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post('/api/bookings/', {
            'listing_id': self.listing.id,
            'date_from': str(datetime.date.today() + datetime.timedelta(days=6)),
            'date_to': str(datetime.date.today() + datetime.timedelta(days=9)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_booking_as_landlord(self):
        """Подтверждение бронирования арендодателем / Approve booking as landlord."""
        self.client.force_authenticate(user=self.landlord)
        response = self.client.post(f'/api/bookings/{self.booking.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.BookingStatus.APPROVED)

    def test_cancel_booking_as_tenant(self):
        """Отмена бронирования арендатором / Cancel booking as tenant."""
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(f'/api/bookings/{self.booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.BookingStatus.CANCELLED)

    def test_cannot_cancel_others_booking(self):
        """Нельзя отменить чужое бронирование / Cannot cancel other's booking."""
        other_tenant = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_tenant)
        response = self.client.post(f'/api/bookings/{self.booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rebook_same_dates_after_cancellation(self):
        """Можно забронировать те же даты после отмены / Can rebook same dates after cancellation."""
        self.client.force_authenticate(user=self.tenant)
        self.client.post(f'/api/bookings/{self.booking.id}/cancel/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.BookingStatus.CANCELLED)
        response = self.client.post('/api/bookings/', {
            'listing_id': self.listing.id,
            'date_from': str(datetime.date.today() + datetime.timedelta(days=5)),
            'date_to': str(datetime.date.today() + datetime.timedelta(days=10)),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)