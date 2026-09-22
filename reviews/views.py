from typing import Any
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from users.permissions import IsOwnerOrReadOnly
from bookings.models import Booking
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Reviews'])
class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления отзывами / Review management ViewSet.

    Только арендаторы с подтверждённым бронированием могут оставлять отзывы.
    Автор может редактировать и удалять свои отзывы.

    Only tenants with confirmed booking can leave reviews.
    Author can edit and delete their reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @extend_schema(
        summary='Список отзывов / Review list',
        description='Возвращает все отзывы. / Returns all reviews.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Создать отзыв / Create review',
        description='Создаёт отзыв. Только для арендаторов с подтверждённым бронированием. / Creates review. Only for tenants with confirmed booking.'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer: Any) -> None:
        """
        Создаёт отзыв если у пользователя есть подтверждённое бронирование.
        Creates review if user has confirmed booking.
        """
        listing = serializer.validated_data['listing']
        has_booking = Booking.objects.filter(
            tenant=self.request.user,
            listing=listing,
            status='approved'
        ).exists()
        if not has_booking:
            raise PermissionDenied('You cannot create a review without a confirmed booking')
        serializer.save(author=self.request.user)

    def get_permissions(self):
        """
        Просмотр доступен всем, изменение только владельцу отзыва.
        Viewing available to all, editing only to review owner.
        """
        if self.action == 'list':
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [IsOwnerOrReadOnly()]