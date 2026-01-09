from django.contrib import admin

from .models import CashierBook


@admin.register(CashierBook)
class CashierBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'cashier', 'cash_drawer', 'time_open', 'time_closed', 'created_at')
    list_filter = ('time_open', 'time_closed', 'created_at')
    search_fields = ('cashier__email', 'cashier__name', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
