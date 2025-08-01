from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('name', 'email', 'gender', 'phone', 'address')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password', 'password2', 'name', 'email', 'gender', 'phone', 'address', 'role'),
        }),
    )
    list_display = ('username', 'name', 'role', 'email', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
