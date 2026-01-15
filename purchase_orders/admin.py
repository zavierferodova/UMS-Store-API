from django.contrib import admin

from purchase_orders.models.po_item import PoItem
from purchase_orders.models.purchase_order import PurchaseOrder


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("code", "requester", "approver", "supplier", "payment_option", "status", "created_at", "updated_at")
    list_filter = ("status", "payment_option")
    search_fields = ("code", "requester__username", "approver__username", "supplier__name")

@admin.register(PoItem)
class PoItemAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase_order", "product_sku", "price", "amounts", "supplier_discount")
    list_filter = ("purchase_order", "product_sku")
    search_fields = ("id", "purchase_order__code", "product_sku__sku")
