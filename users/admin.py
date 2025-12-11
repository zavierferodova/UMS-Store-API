from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as DefaultUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm

from .models import User


class UserChangeForm(DefaultUserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

class UserCreationForm(DefaultUserCreationForm):
    class Meta:
        model = User
        fields = ["email"]

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('Account', {'fields': ('email', 'username', 'password')}),
        ('Personal Information', {'fields': ('name', 'gender', 'phone', 'address')}),
        ('Additional Information    ', {'fields': ('created_at', 'updated_at')}),
        ('App Permissions', {'fields': ('role',)}),
        ('Admin Panel Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'name'),
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('name', 'email', 'username', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('username', 'name', 'email')
    ordering = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')

admin.site.register(User, UserAdmin)
