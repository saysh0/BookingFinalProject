from typing import Any
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import QuerySet
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from users.permissions import IsTenantOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone

@extend_schema(tags=['Bookings'])
class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления бронированиями / Booking management ViewSet.

    Арендатор может создавать и просматривать свои бронирования.
    Арендодатель может подтверждать или отклонять запросы на бронирование.

    Tenant can create and view their bookings.
    Landlord can approve or reject booking requests.
    """
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing']
    ordering_fields = ['created_at', 'date_from', 'date_to']

    @extend_schema(
        summary='Список бронирований / Booking list',
        description='Возвращает бронирования текущего пользователя как арендатора и арендодателя. / Returns current user bookings as tenant and landlord.',
        parameters=[
            OpenApiParameter(name='status',
                             description='Фильтр по статусу / Filter by status: in_progress, approved, rejected',
                             required=False, type=str),
            OpenApiParameter(name='ordering', description='Сортировка / Ordering: created_at, date_from, date_to',
                             required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Создать бронирование / Create booking',
        description='Создаёт бронирование на указанные даты. Максимум 30 дней. / Creates booking for specified dates. Maximum 30 days.'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)



    def get_queryset(self) -> QuerySet:
        """
        Возвращает бронирования текущего пользователя как арендатора и арендодателя.
        Returns current user bookings both as tenant and landlord.
        """
        user = self.request.user
        from django.db.models import Q
        return Booking.objects.filter(Q(listing__owner=user) | Q(tenant=user))

    def perform_create(self, serializer: Any) -> None:
        """
        Автоматически устанавливает арендатора при создании бронирования.
        Automatically sets tenant on booking creation.
        """
        serializer.save(tenant=self.request.user)

    def get_permissions(self) -> list[Any]:
        """
        Изменение и удаление только для владельца бронирования.
        Update and delete only for booking owner.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsTenantOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        summary='Подтвердить бронирование / Approve booking',
        description='Подтверждает бронирование. Только для владельца объявления. / Approves booking. Listing owner only.'
    )
    @action(detail=True, methods=['post'])
    def approve(self, request: Request, pk: int | None = None) -> Response:
        """
        Подтверждает бронирование / Approves booking.

        Доступно только владельцу объявления.
        Available only to listing owner.
        """
        booking = self.get_object()
        if booking.listing.owner != request.user:
            return Response({'error': 'You are not the owner'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != Booking.BookingStatus.IN_PROGRESS:
            return Response({'error': 'Booking is not in progress'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.BookingStatus.APPROVED
        booking.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


    @extend_schema(
        summary='Отклонить бронирование / Reject booking',
        description='Отклоняет бронирование. Только для владельца объявления. / Rejects booking. Listing owner only.'
    )
    @action(detail=True, methods=['post'])
    def reject(self, request: Request, pk: int | None = None) -> Response:
        """
        Отклоняет бронирование / Rejects booking.

        Доступно только владельцу объявления.
        Available only to listing owner.
        """
        booking = self.get_object()
        if booking.listing.owner != request.user:
            return Response({'error': 'You are not the owner'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != Booking.BookingStatus.IN_PROGRESS:
            return Response({'error': 'Booking is not in progress'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.BookingStatus.REJECTED
        booking.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


    @extend_schema(
        summary='Отменить бронирование / Cancel booking',
        description='Отменяет бронирование. Только до даты заезда. / Cancels booking. Only before check-in date.'
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request: Request, pk: int | None = None) -> Response:
        """
        Отменяет бронирование / Cancels booking.

        Доступно только арендатору до даты заезда.
        Available only to tenant before check-in date.
        """
        booking = self.get_object()
        if booking.tenant != request.user:
            return Response({'error': 'You are not the tenant'}, status=status.HTTP_403_FORBIDDEN)

        if booking.date_from <= timezone.now().date():
            return Response({'error': 'Cannot cancel after check-in date'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.status not in (Booking.BookingStatus.IN_PROGRESS, Booking.BookingStatus.APPROVED):
            return Response({'error': 'Booking is not in progress'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.BookingStatus.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)