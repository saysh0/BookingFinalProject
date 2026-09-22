from django.utils import timezone
from rest_framework import serializers, request
from bookings.models import Booking
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from listings.serializers import ListingSerializer
from reviews.models import Review
from listings.models import Listing

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзыва / Review serializer.

    Возвращает данные отзыва с вложенными данными автора и объявления.
    Returns review data with nested author and listing data.
    """
    author = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'listing', 'listing_id', 'rating', 'text', 'created_at')
        extra_kwargs = {'created_at': {'read_only': True}}

    def validate(self, data):
        author = self.context['request'].user
        listing = data['listing']
        booking = Booking.objects.filter(
            tenant=author,
            listing=listing,
            status=Booking.BookingStatus.APPROVED,
            date_to__lt=timezone.now().date(),
        )

        if not booking.exists():
            raise serializers.ValidationError('Booking does not exist')

        if Review.objects.filter(author=self.context['request'].user, listing=data['listing']).exists():
            raise serializers.ValidationError('You already reviewed this listing')
        return data


