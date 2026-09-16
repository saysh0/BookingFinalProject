from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from listings.models import Listing

User = get_user_model()

location_validator = RegexValidator(regex=r'^[А-Яа-яA-Za-z\s]+,\s[А-Яа-яA-Za-z\s]+\s\d+$', message='Format: City, Street number of the steer. Example: Berlin, Hauptstraße 5')
class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    location = serializers.CharField(validators=[location_validator])
    class Meta:
        model = Listing
        fields = ('id', 'owner', 'title', 'location', 'description', 'price', 'rooms', 'housing_type', 'is_active', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}