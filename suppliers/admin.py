from django.contrib import admin

from suppliers.models.payment import SupplierPayment
from suppliers.models.supplier import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {'fields': ('id', 'code', 'name', 'address', 'phone', 'email', 'is_deleted')}),
        ('Transaction', {'fields': ('discount', )}),
        ('Additional Information', {'fields': ('created_at', 'updated_at')}),
    )
    list_display = ('code', 'name', 'address', 'phone', 'email', 'discount', 'is_deleted', 'created_at', 'updated_at')
    readonly_fields = ('id', 'code', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'address')

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {'fields': ('supplier', 'name', 'owner', 'account_number')}),
        ('Additional Information', {'fields': ('created_at', 'updated_at')}),
    )
    list_display = ('supplier_payment_id', 'name', 'owner', 'account_number', 'supplier_code', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    search_fields = ('name', 'owner', 'account_number')

    def supplier_code(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        supplier = obj.supplier
        if supplier:
            url = reverse('admin:suppliers_supplier_change', args=[supplier.pk])
            return format_html('<a href="{}">{}</a>', url, supplier.code)
        return "-"
    supplier_code.short_description = 'Supplier Code'

    def supplier_payment_id(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        url = reverse('admin:suppliers_supplierpayment_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.id)
    supplier_payment_id.short_description = 'ID'
