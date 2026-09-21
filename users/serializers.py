from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя / User registration serializer.

    Принимает username, email, password и group (Landlord/Tenant).
    Хеширует пароль и назначает группу при создании.

    Accepts username, email, password and group (Landlord/Tenant).
    Hashes password and assigns group on creation.
    """
    GROUP_CHOICES = [
        ('Landlord', 'Арендодатель'),
        ('Tenant', 'Арендатор'),
    ]

    groups = serializers.MultipleChoiceField(choices=GROUP_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: dict[str, Any]) -> User:
        """
        Создаёт пользователя с хешированным паролем и назначает группу.
        Creates user with hashed password and assigns group.
        """
        password = validated_data.pop('password')
        group_names = validated_data.pop('groups')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        for group_name in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных пользователя / User read serializer.

    Возвращает основные данные пользователя без пароля.
    Returns basic user data without password.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения JWT токена / Custom JWT token serializer.

    Использует email вместо username для аутентификации.
    Uses email instead of username for authentication.
    """
    username_field = 'email'