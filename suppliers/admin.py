from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'address', 'phone', 'email', 'discount', 'created_at', 'updated_at')
    fields = ('code', 'name', 'address', 'phone', 'email', 'discount', 'is_deleted')
    readonly_fields = ('code',)
    search_fields = ('name', 'email', 'address')