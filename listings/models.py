from django.db import models
from djmoney.models.fields import MoneyField
from django.core.validators import MinValueValidator
from django.conf import settings

# Create your models here.

class Listing(models.Model):
    class HousingType(models.TextChoices):
        APARTMENT = 'apartment', 'квартира'
        HOUSE = 'house', 'дом'
        STUDIO = 'studio', 'студия'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=60)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default_currency='EUR')
    rooms = models.PositiveIntegerField(default=1)
    housing_type = models.CharField(choices=HousingType.choices, max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Listing: {self.title}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'