from rest_framework import serializers
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from history.models import ViewHistory, SearchHistory
from listings.serializers import ListingSerializer

User = get_user_model()

class SearchHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = SearchHistory
        fields = ('id', 'user', 'search_text', 'search_date')
        extra_kwargs = {'search_date': {'read_only': True}}


class ViewHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = ViewHistory
        fields = ('id', 'user', 'listing', 'viewed_at')
        extra_kwargs = {'viewed_at': {'read_only': True}}