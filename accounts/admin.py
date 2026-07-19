from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from auction_project.admin import admin_site
from .models import Profile


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_per_page = 20


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'phone', 'city', 'state', 'is_seller',
        'created_at', 'updated_at',
    ]
    list_filter = ['is_seller', 'city', 'state', 'created_at']
    search_fields = [
        'user__username', 'user__email', 'user__first_name',
        'user__last_name', 'phone', 'city',
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Contact', {
            'fields': ('phone', 'address', 'city', 'state', 'zip_code'),
        }),
        ('Profile', {
            'fields': ('is_seller', 'profile_image'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


admin_site.register(User, UserAdmin)
admin_site.register(Profile, ProfileAdmin)
