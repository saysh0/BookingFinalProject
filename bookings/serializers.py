from django.utils import timezone
from rest_framework import serializers
from . import models
from listings.serializers import ListingSerializer
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

class BookingSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = models.Booking
        fields = ('id', 'tenant', 'listing', 'status', 'date_from', 'date_to', 'created_at', 'updated_at')
        extra_kwargs = {'status': {'read_only': True}}

    def validate(self, data):
        if data['date_from'] >= data['date_to']:
            raise serializers.ValidationError('Date must be after date')
        if data['date_from'] < timezone.now().date():
            raise serializers.ValidationError("Date can't be in the past")
        duration = data['date_to'] - data['date_from']
        if duration.days > 30:
            raise serializers.ValidationError('Date must be 30days or less than 30 days')
        overlapping = models.Booking.objects.filter(listing=data['listing'], date_from__lt=data['date_to'], date_to__gt=data['date_from'])
        if overlapping.exists():
            raise serializers.ValidationError('These dates are already taken')
        return data