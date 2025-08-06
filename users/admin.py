from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('name', 'gender', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password', 'password2', 'name', 'username', 'gender', 'phone', 'address'),
        }),
    )
    list_display = ('name', 'email', 'username', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('username', 'name', 'email')
    ordering = ('name',)

admin.site.register(User, UserAdmin)
