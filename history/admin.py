from django.contrib import admin
from history.models import ViewHistory, SearchHistory

# Register your models here.

class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'viewed_at')
    search_fields = ('user__username', 'user__email', 'listing__title')
    list_filter = ('viewed_at',)

admin.site.register(ViewHistory, ViewHistoryAdmin)

class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_text', 'search_date')
    search_fields = ('user__username', 'search_text')
    list_filter = ('search_date',)

admin.site.register(SearchHistory, SearchHistoryAdmin)