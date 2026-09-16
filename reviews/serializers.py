from rest_framework import serializers
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from listings.serializers import ListingSerializer
from reviews.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзыва / Review serializer.

    Возвращает данные отзыва с вложенными данными автора и объявления.
    Returns review data with nested author and listing data.
    """
    author = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'author', 'listing', 'rating', 'text', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}