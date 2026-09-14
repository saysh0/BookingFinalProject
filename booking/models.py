from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField


class User(AbstractUser):
    class Role(models.TextChoices):
        TENANT = 'tenant', 'арендатор'
        LANDLORD = 'landlord', 'арендодатель'

    role = models.CharField(choices=Role.choices, default=Role.TENANT, max_length=15)

    def __str__(self):
        return f'User: {self.username}, UserRole: {self.role}'


class Listing(models.Model):
    class HousingType(models.TextChoices):
        APARTMENT = 'apartment', 'квартира'
        HOUSE = 'house', 'дом'
        STUDIO = 'studio', 'студия'

    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=60)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
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


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'в процессе'
        APPROVED = 'approved', 'одобрено'
        REJECTED = 'rejected', 'отклоненно'

    tenant = models.ForeignKey(User, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(choices=BookingStatus.choices, max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Booking: {self.listing.title}'


    class Meta:
        unique_together = [['tenant', 'listing', 'date_from', 'date_to']]
        ordering = ['-date_from', '-date_to']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    @property
    def owner(self):
        return self.tenant


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ReviewAuthor: {self.author}'

    class Meta:
        unique_together = [['author', 'listing']]
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    @property
    def owner(self):
        return self.author


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    search_text = models.CharField(max_length=50)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'SearchHistory: {self.search_text}'

    class Meta:
        ordering = ['-search_date']


class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ViewHistory: {self.viewed_at}'

    class Meta:
        ordering = ['-viewed_at']
