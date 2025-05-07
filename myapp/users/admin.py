from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """Custom admin view for User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('bio', 'profile_picture')}),
    )

admin.site.register(User, CustomUserAdmin) 