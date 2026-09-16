from django.contrib import admin
from bookings.models import Booking

# Register your models here.

class BookingAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'listing', 'date_from', 'date_to', 'status', 'created_at', 'updated_at')
    search_fields = ('tenant__username', 'tenant__email', 'listing__title', 'status', 'created_at', 'updated_at', 'date_from', 'date_to')
    list_filter = ('created_at', 'updated_at', 'status', 'date_to', 'date_from')

admin.site.register(Booking, BookingAdmin)