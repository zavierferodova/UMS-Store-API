from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {'fields': ('code', 'name', 'address', 'phone', 'email')}),
        ('Transaction', {'fields': ('discount', )}),
        ('Additional Information', {'fields': ('is_deleted', 'created_at', 'updated_at')}),
    )
    list_display = ('code', 'name', 'address', 'phone', 'email', 'discount', 'created_at', 'updated_at')
    readonly_fields = ('id', 'code', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'address')