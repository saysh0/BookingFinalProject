from django.db import models
from django.conf import settings
from listings.models import Listing


class SearchHistory(models.Model):
    """
    Модель истории поиска / Search history model.

    Сохраняет ключевые слова поиска пользователя для отображения популярных запросов.
    Saves user search keywords to display popular queries.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    search_text = models.CharField(max_length=50)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает текст поискового запроса / Returns search query text."""
        return f'SearchHistory: {self.search_text}'

    class Meta:
        ordering = ['-search_date']


class ViewHistory(models.Model):
    """
    Модель истории просмотров / View history model.

    Сохраняет информацию о просмотрах объявлений для отображения популярных объявлений.
    Saves listing view information to display popular listings.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает дату просмотра / Returns view date."""
        return f'ViewHistory: {self.viewed_at}'

    class Meta:
        ordering = ['-viewed_at']