from django.db import models
from django.conf import settings
from listings.models import Listing
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Модель отзыва об объявлении / Listing review model.

    Только арендаторы с подтверждённым бронированием могут оставлять отзывы.
    Один пользователь может оставить только один отзыв на объявление.

    Only tenants with confirmed booking can leave reviews.
    One user can leave only one review per listing.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает автора отзыва / Returns review author."""
        return f'ReviewAuthor: {self.author}'

    class Meta:
        unique_together = [['author', 'listing']]
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'