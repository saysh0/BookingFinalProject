from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя / Custom user model.

    Использует email вместо username для аутентификации.
    Роли управляются через Django Groups (Landlord/Tenant).

    Uses email instead of username for authentication.
    Roles are managed through Django Groups (Landlord/Tenant).
    """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        """Возвращает email пользователя / Returns user email."""
        return f'User email: {self.email}'