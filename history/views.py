from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins, filters
from rest_framework.response import Response
from history.models import SearchHistory, ViewHistory
from history.serializers import SearchHistorySerializer, ViewHistorySerializer

# Create your views here.

class SearchHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SearchHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['search_text']
    ordering_fields = ['search_date']

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)

class ViewHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ViewHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['listing__title']
    ordering_fields = ['viewed_at']

    def get_queryset(self):
        return ViewHistory.objects.filter(user=self.request.user)