import django_filters
from listings.models import Listing


class ListingFilter(django_filters.FilterSet):
    """
    Фильтр для объявлений / Listing filter.

    Поддерживает фильтрацию по диапазону цены, количеству комнат, типу жилья и локации.
    Supports filtering by price range, number of rooms, housing type and location.
    """
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')

    class Meta:
        model = Listing
        fields = ['housing_type', 'location', 'is_active']