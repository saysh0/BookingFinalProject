from django.contrib import admin
from reviews.models import Review

# Register your models here.

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'listing', 'rating', 'created_at')
    search_fields = ('author__username', 'listing__title', 'text')
    list_filter = ('rating', 'created_at')

admin.site.register(Review, ReviewAdmin)
