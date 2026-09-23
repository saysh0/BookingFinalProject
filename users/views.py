from typing import Any
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from listings.serializers import ListingSerializer
from users.permissions import IsSelfOrReadOnly
from users.serializers import UserCreateSerializer, UserSerializer
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomTokenObtainPairSerializer


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями / User management ViewSet.

    Поддерживает регистрацию и просмотр профиля.
    Регистрация доступна всем, остальные действия только авторизованным.

    Supports registration and profile viewing.
    Registration is open to all, other actions require authentication.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary='Регистрация / Registration',
        description='Создаёт нового пользователя с выбором роли (Landlord/Tenant). / Creates new user with role selection (Landlord/Tenant).'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_serializer_class(self) -> type[Serializer]:
        """
        Возвращает сериализатор в зависимости от действия.
        Returns serializer based on action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Регистрация доступна всем, остальное только авторизованным.
        Registration is open to all, rest requires authentication.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsSelfOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        summary='Профиль пользователя / User profile',
        description='Возвращает профиль текущего пользователя с его объявлениями и бронированиями. / Returns current user profile with listings and bookings.'
    )
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Возвращает профиль текущего пользователя с его листингами и бронированиями.
        Returns current user profile with their listings and bookings.
        """
        user = request.user
        return Response({
            'user': UserSerializer(user).data,
            'listings': ListingSerializer(user.listings.all(), many=True).data,
            'bookings': BookingSerializer(user.bookings.all(), many=True).data,
        })


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомный эндпоинт для получения JWT токена / Custom JWT token endpoint.

    Принимает email и пароль вместо username и пароля.
    Accepts email and password instead of username and password.
    """
    serializer_class = CustomTokenObtainPairSerializer