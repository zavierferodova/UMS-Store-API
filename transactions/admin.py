from django.contrib import admin

from .models import Transaction, TransactionCoupon, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0

class TransactionCouponInline(admin.TabularInline):
    model = TransactionCoupon
    extra = 0

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('code', 'cashier', 'total', 'payment', 'created_at')
    list_filter = ('payment', 'created_at', 'cashier')
    search_fields = ('code', 'cashier__username', 'note')
    inlines = [TransactionItemInline, TransactionCouponInline]
    readonly_fields = ('code', 'created_at', 'updated_at')

@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'product_sku', 'amount', 'unit_price')
    search_fields = ('transaction__code', 'product_sku__sku')

@admin.register(TransactionCoupon)
class TransactionCouponAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'coupon_code')
    search_fields = ('transaction__code', 'coupon_code__code')
