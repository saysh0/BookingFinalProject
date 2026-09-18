from typing import Any
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from history.models import ViewHistory, SearchHistory
from listings.models import Listing, ListingImage
from listings.serializers import ListingSerializer, ListingImageSerializer
from users.permissions import IsLandlord, IsOwnerOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from listings.filters import ListingFilter
from django.db.models import Count, QuerySet


@extend_schema(tags=['Listings'])
class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления объявлениями / Listing management ViewSet.

    Поддерживает создание, редактирование, удаление и просмотр объявлений.
    Включает управление фотографиями и историю просмотров/поиска.
    Только арендодатели могут создавать и редактировать объявления.

    Supports creating, editing, deleting and viewing listings.
    Includes image management and view/search history.
    Only landlords can create and edit listings.
    """

    serializer_class = ListingSerializer
    permission_classes = [IsLandlord, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price', 'rooms', 'views_count']
    queryset = Listing.objects.none()

    def get_queryset(self) -> QuerySet:
        """
        Возвращает активные объявления с количеством просмотров.
        Returns active listings with view count annotation.
        """
        from django.db.models import Count
        return Listing.objects.filter(is_active=True).annotate(views_count=Count('views'))

    def perform_create(self, serializer: Any) -> None:
        """
        Автоматически устанавливает владельца объявления при создании.
        Automatically sets listing owner on creation.
        """
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary='Детали объявления / Listing details',
        description='Возвращает детали объявления и записывает просмотр в историю. / Returns listing details and saves view to history.'
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Возвращает объявление и записывает просмотр в историю.
        Returns listing and saves view to history.
        """
        instance = self.get_object()
        if request.user.is_authenticated:
            ViewHistory.objects.create(user=request.user, listing=instance)
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='Список объявлений / List of listings',
        description='Возвращает список активных объявлений с фильтрацией, поиском и сортировкой. / Returns list of active listings with filtering, search and ordering.',
        parameters=[
            OpenApiParameter(name='search',
                             description='Поиск по названию, описанию и локации / Search by title, description and location',
                             required=False, type=str),
            OpenApiParameter(name='housing_type', description='Тип жилья / Housing type', required=False, type=str),
            OpenApiParameter(name='price_min', description='Минимальная цена / Minimum price', required=False,
                             type=float),
            OpenApiParameter(name='price_max', description='Максимальная цена / Maximum price', required=False,
                             type=float),
            OpenApiParameter(name='rooms_min', description='Минимальное количество комнат / Minimum rooms',
                             required=False, type=int),
            OpenApiParameter(name='rooms_max', description='Максимальное количество комнат / Maximum rooms',
                             required=False, type=int),
            OpenApiParameter(name='ordering',
                             description='Сортировка / Ordering: price, -price, created_at, -created_at, views_count, -views_count',
                             required=False, type=str),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Возвращает список объявлений и сохраняет поисковый запрос в историю.
        Returns listing list and saves search query to history.
        """
        search = request.query_params.get('search')
        if search and request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, search_text=search)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Фото объявления / Listing images',
        description='GET - список фото, POST - загрузить фото (макс 15). / GET - image list, POST - upload image (max 15).'
    )
    @action(detail=True, methods=['get', 'post'], url_path='images')
    def images(self, request: Request, pk: int | None = None) -> Response:
        """
        Получение и загрузка фотографий объявления / Get and upload listing images.

        GET - возвращает все фото объявления / returns all listing photos.
        POST - загружает новое фото (максимум 15) / uploads new photo (max 15).
        """
        listing = self.get_object()
        if request.method == 'GET':
            images = ListingImage.objects.filter(listing=listing).order_by('order')
            serializer = ListingImageSerializer(images, many=True)
            return Response(serializer.data)
        if request.method == 'POST':
            if request.user != listing.owner:
                return Response({'detail': 'You are not owner this listing'}, status=status.HTTP_403_FORBIDDEN)
            if ListingImage.objects.filter(listing=listing).count() > 15:
                raise ValidationError({'detail': 'This listing has more than 15 images'})
            serializer = ListingImageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(listing=listing)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Удалить фото / Delete image',
        description='Удаляет фото объявления. Только для владельца. / Deletes listing image. Owner only.'
    )
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request: Request, pk: int | None = None, image_id: int | None = None) -> Response:
        """
        Удаляет фотографию объявления / Deletes listing image.

        Доступно только владельцу объявления.
        Available only to listing owner.
        """
        listing = self.get_object()
        if request.user != listing.owner:
            return Response({'detail': 'You are not owner'}, status=status.HTTP_403_FORBIDDEN)
        image = get_object_or_404(ListingImage, pk=image_id, listing=listing)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary='Обновить порядок фото / Update image order',
        description='Обновляет порядок фото объявления. Только для владельца. / Updates listing image order. Owner only.'
    )
    @action(detail=True, methods=['patch'], url_path='images/(?P<image_id>[^/.]+)')
    def update_image(self, request: Request, pk: int | None = None, image_id: int | None = None) -> Response:
        """
        Обновляет порядок фотографии объявления / Updates listing image order.

        Доступно только владельцу объявления.
        Available only to listing owner.
        """
        listing = self.get_object()
        if request.user != listing.owner:
            return Response({'detail': 'You are not owner this listing'}, status=status.HTTP_403_FORBIDDEN)
        image = get_object_or_404(ListingImage, pk=image_id, listing=listing)
        serializer = ListingImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Обновить объявление / Update listing',
        description='Обновляет все поля объявления. Только для владельца. / Updates all listing fields. Owner only.'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary='Частичное обновление / Partial update',
        description='Обновляет отдельные поля объявления. Только для владельца. / Updates specific listing fields. Owner only.'
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary='Удалить объявление / Delete listing',
        description='Удаляет объявление из базы данных. Только для владельца. / Deletes listing from database. Owner only.'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary='Создать объявление / Create listing',
        description='Создаёт новое объявление. Только для арендодателей. / Creates new listing. Landlords only.'
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().create(request, *args, **kwargs)