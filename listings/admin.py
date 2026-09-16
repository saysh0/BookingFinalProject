from django.contrib import admin
from listings.models import Listing

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'location', 'price', 'rooms', 'housing_type', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'location', 'owner__username')
    list_filter = ('is_active', 'housing_type', 'rooms', 'created_at')

admin.site.register(Listing, ListingAdmin)