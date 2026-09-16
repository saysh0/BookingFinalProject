from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from history.models import ViewHistory, SearchHistory
from listings.models import Listing
from listings.serializers import ListingSerializer
from users.permissions import IsLandlord, IsOwnerOrReadOnly

# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['housing_type', 'rooms', 'location']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price', 'rooms']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            ViewHistory.objects.create(user=request.user, listing=instance)
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        if search and request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, search_text=search)
        return super().list(request, *args, **kwargs)
