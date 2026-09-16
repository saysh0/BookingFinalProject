from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins, filters
from django.db.models import QuerySet
from history.models import SearchHistory, ViewHistory
from history.serializers import SearchHistorySerializer, ViewHistorySerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['History'])
class SearchHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для истории поиска / Search history ViewSet.

    Только чтение — показывает историю поисковых запросов текущего пользователя.
    Read only — shows search query history of current user.
    """
    serializer_class = SearchHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['search_text']
    ordering_fields = ['search_date']

    @extend_schema(
        summary='История поиска / Search history',
        description='Возвращает историю поисковых запросов текущего пользователя. / Returns search query history of current user.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """
        Возвращает историю поиска текущего пользователя.
        Returns search history of current user.
        """
        return SearchHistory.objects.filter(user=self.request.user)

@extend_schema(tags=['History'])
class ViewHistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для истории просмотров / View history ViewSet.

    Только чтение — показывает историю просмотров объявлений текущего пользователя.
    Read only — shows listing view history of current user.
    """
    serializer_class = ViewHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['listing__title']
    ordering_fields = ['viewed_at']

    @extend_schema(
        summary='История просмотров / View history',
        description='Возвращает историю просмотров объявлений текущего пользователя. / Returns listing view history of current user.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """
        Возвращает историю просмотров текущего пользователя.
        Returns view history of current user.
        """
        return ViewHistory.objects.filter(user=self.request.user)