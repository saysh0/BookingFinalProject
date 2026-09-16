from django.db import models
from django.conf import settings
from listings.models import Listing

# Create your models here.

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    search_text = models.CharField(max_length=50)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'SearchHistory: {self.search_text}'

    class Meta:
        ordering = ['-search_date']


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ViewHistory: {self.viewed_at}'

    class Meta:
        ordering = ['-viewed_at']