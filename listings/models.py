from django.db import models
from djmoney.models.fields import MoneyField
from django.core.validators import MinValueValidator
from django.conf import settings


class Listing(models.Model):
    """
    Модель объявления о сдаче жилья / Housing listing model.

    Содержит информацию о жилье: заголовок, описание, цену, местоположение.
    Только арендодатели могут создавать и управлять объявлениями.

    Contains housing information: title, description, price, location.
    Only landlords can create and manage listings.
    """

    class HousingType(models.TextChoices):
        """Тип жилья / Housing type."""
        APARTMENT = 'apartment', 'квартира'
        HOUSE = 'house', 'дом'
        STUDIO = 'studio', 'студия'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='listings')
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=60)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default_currency='EUR')
    rooms = models.PositiveIntegerField(default=1)
    housing_type = models.CharField(choices=HousingType.choices, max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Возвращает заголовок объявления / Returns listing title."""
        return f'Listing: {self.title}'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location'], name='listing_location_idx'),
            models.Index(fields=['is_active', 'housing_type'], name='listing_active_type_idx'),
            models.Index(fields=['location', 'is_active'], name='listing_location_active_idx'),
            models.Index(fields=['-created_at'], name='listing_created_at_idx'),
        ]
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class ListingImage(models.Model):
    """
    Модель фотографии объявления / Listing image model.

    Хранит фотографии объявления с возможностью сортировки по порядку.
    Максимум 15 фотографий на одно объявление.

    Stores listing photos with ordering support.
    Maximum 15 photos per listing.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает название объявления и путь к фото / Returns listing title and image path."""
        return f'Listing images: {self.listing.title} {self.image}'

    class Meta:
        ordering = ['order']
        verbose_name = 'Фото'
        verbose_name_plural = 'Фотографии'