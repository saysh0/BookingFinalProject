from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.models import Booking
from bookings.serializers import BookingSerializer
from users.permissions import IsOwnerOrReadOnly

# Create your views here.

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing']
    ordering_fields = ['created_at', 'date_from', 'date_to']

    def get_queryset(self):
        user = self.request.user
        from django.db.models import Q
        return Booking.objects.filter(Q(listing__owner=user) | Q(tenant=user))

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk):
        booking = self.get_object()
        if booking.listing.owner == request.user:
            booking.status = Booking.BookingStatus.APPROVED
            booking.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
        return Response({'error': 'You are not the owner'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk):
        booking = self.get_object()
        if booking.listing.owner == request.user:
            booking.status = Booking.BookingStatus.REJECTED
            booking.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
        return Response({'error': 'You are not the owner'}, status=status.HTTP_403_FORBIDDEN)


