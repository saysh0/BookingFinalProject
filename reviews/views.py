from rest_framework import viewsets, permissions, filters
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from users.permissions import IsOwnerOrReadOnly
from bookings.models import Booking
from rest_framework.exceptions import PermissionDenied

# Create your views here.

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']
        has_booking = Booking.objects.filter(tenant=self.request.user, listing=listing, status='approved').exists()
        if not has_booking:
            raise PermissionDenied('You cannot create booking')
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [IsOwnerOrReadOnly()]

