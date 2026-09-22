from django.db import models
from django.conf import settings
from listings.models import Listing
from django.db.models import Q, UniqueConstraint


class Booking(models.Model):
    """
    Модель бронирования жилья / Housing booking model.

    Связывает арендатора с объявлением на определённые даты.
    Арендодатель может подтверждать или отклонять бронирования.

    Links tenant with a listing for specific dates.
    Landlord can approve or reject bookings.
    """

    class BookingStatus(models.TextChoices):
        """Статусы бронирования / Booking statuses."""
        IN_PROGRESS = 'in_progress', 'в процессе'
        APPROVED = 'approved', 'одобрено'
        REJECTED = 'rejected', 'отклоненно'
        CANCELLED = 'cancelled', 'отменено арендатором'

    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(
        choices=BookingStatus.choices,
        max_length=15,
        default=BookingStatus.IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Возвращает название объявления / Returns listing title."""
        return f'Booking: {self.listing.title}'

    class Meta:
        ordering = ['-date_from', '-date_to']
        constraints = [
            UniqueConstraint(
                fields=['tenant', 'listing', 'date_from', 'date_to'],
                condition=~Q(status='cancelled') & ~Q(status='rejected'),
                name='unique_active_booking'
            )
        ]
        indexes = [
            models.Index(fields=['listing', 'date_from', 'date_to'], name='booking_listing_dates_idx'),
            models.Index(fields=['tenant', 'status'], name='booking_tenant_status_idx'),
        ]
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'