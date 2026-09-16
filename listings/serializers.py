from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from listings.models import Listing, ListingImage

User = get_user_model()

location_validator = RegexValidator(
    regex=r'^[А-Яа-яA-Za-z\s]+,\s[А-Яа-яA-Za-z\s]+\s\d+$',
    message='Format: City, Street number. Example: Berlin, Hauptstraße 5'
)


class ListingSerializer(serializers.ModelSerializer):
    """
    Сериализатор объявления / Listing serializer.

    Включает валидацию формата адреса через regex.
    Владелец подставляется автоматически из токена.

    Includes address format validation via regex.
    Owner is set automatically from token.
    """
    owner = UserSerializer(read_only=True)
    location = serializers.CharField(validators=[location_validator])

    class Meta:
        model = Listing
        fields = ('id', 'owner', 'title', 'location', 'description', 'price', 'rooms', 'housing_type', 'is_active',
                  'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}


class ListingImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор фотографий объявления / Listing image serializer.

    Управляет загрузкой и порядком фотографий объявления.
    Manages listing photo upload and ordering.
    """

    class Meta:
        model = ListingImage
        fields = ('id', 'image', 'order', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}