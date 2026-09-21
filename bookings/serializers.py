from typing import Any
from django.utils import timezone
from rest_framework import serializers
from bookings.models import Booking
from listings.serializers import ListingSerializer
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from listings.models import Listing

User = get_user_model()


class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для бронирований / Booking serializer.

    Включает валидацию дат: проверка прошлого, длительности и пересечений.
    Includes date validation: past dates, duration and overlap checks.
    """
    tenant = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = ('id', 'tenant', 'listing', 'listing_id', 'status', 'date_from', 'date_to', 'created_at', 'updated_at')
        extra_kwargs = {'status': {'read_only': True}}

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Валидирует даты бронирования / Validates booking dates.

        Проверяет:
        - дата заезда раньше даты выезда
        - даты не в прошлом
        - длительность не более 30 дней
        - отсутствие пересечений с существующими бронированиями
        - арендатор не является владельцем объявления

        Checks:
        - check-in date is before check-out date
        - dates are not in the past
        - duration is not more than 30 days
        - no overlap with existing bookings
        - tenant is not the listing owner
        """
        if data['date_from'] >= data['date_to']:
            raise serializers.ValidationError('Date must be after date')

        if data['date_from'] < timezone.now().date():
            raise serializers.ValidationError("Date can't be in the past")

        duration = data['date_to'] - data['date_from']
        if duration.days > 30:
            raise serializers.ValidationError('Date must be 30 days or less')

        overlapping = Booking.objects.filter(
            listing=data['listing'],
            date_from__lt=data['date_to'],
            date_to__gt=data['date_from']
        ).exclude(status=Booking.BookingStatus.REJECTED)

        if overlapping.exists():
            raise serializers.ValidationError('These dates are already taken')

        request = self.context.get('request')
        if request and request.user == data['listing'].owner:
            raise serializers.ValidationError('You cant book your own listing')
        return data