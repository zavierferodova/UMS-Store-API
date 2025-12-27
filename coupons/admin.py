from django.contrib import admin

from .models.coupon import Coupon
from .models.coupon_code import CouponCode


class CouponCodeInline(admin.TabularInline):
    model = CouponCode
    extra = 0

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'voucher_value', 'discount_percentage', 'start_time', 'end_time')
    list_filter = ('type', 'start_time', 'end_time')
    search_fields = ('name',)
    inlines = [CouponCodeInline]

@admin.register(CouponCode)
class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'coupon', 'stock')
    search_fields = ('code', 'coupon__name')
    list_filter = ('coupon',)
