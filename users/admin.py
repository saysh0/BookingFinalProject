from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

# Register your models here.

class CustomerUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('groups', 'is_staff')

admin.site.register(User, CustomerUserAdmin)


