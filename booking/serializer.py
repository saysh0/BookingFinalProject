from rest_framework import serializers
from django.core.validators import RegexValidator
from . import models

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = models.User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'username', 'email', 'role')

location_validator = RegexValidator(regex=r'^[А-Яа-яA-Za-z\s]+,\s[А-Яа-яA-Za-z\s]+\s\d+$', message='Format: City, Street number of the steer. Example: Berlin, Hauptstraße 5')
class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    location = serializers.CharField(validators=[location_validator])
    class Meta:
        model = models.Listing
        fields = ('id', 'owner', 'title', 'location', 'description', 'price', 'rooms', 'housing_type', 'is_active', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True},}


class BookingSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = models.Booking
        fields = ('id', 'tenant', 'listing', 'status', 'date_from', 'date_to','created_at')
        extra_kwargs = {'status': {'read_only': True},}

    def validate(self, data):
        if data['date_from'] >= data['date_to']:
            raise serializers.ValidationError('Date must be after date')
        overlapping = models.Booking.objects.filter(listing=data['listing'], date_from__lt=data['date_to'], date_to__gt=data['date_from'])
        if overlapping.exists():
            raise serializers.ValidationError('These dates are already taken')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = models.Review
        fields = ('id', 'author', 'listing', 'rating', 'text', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}


class SearchHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = models.SearchHistory
        fields = ('id', 'user', 'search_text', 'search_date')
        extra_kwargs = {'search_date': {'read_only': True}}


class ViewHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = models.ViewHistory
        fields = ('id', 'user', 'listing', 'viewed_at')
        extra_kwargs = {'viewed_at': {'read_only': True}}