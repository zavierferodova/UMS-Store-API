from django.contrib import admin

from products.models.category import ProductCategory
from products.models.image import ProductImage
from products.models.product import Product
from products.models.sku import ProductSKU


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('filename', 'order_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {'fields': ('id', 'name',)}),
        ('Additional Information', {'fields': ('created_at', 'updated_at')})
    )
    list_display = ('id', 'name', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    search_fields = ('name',)

class ProductSKUInline(admin.TabularInline):
    model = ProductSKU
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {
            'fields': ('id', 'name', 'description', 'price', 'category', 'additional_info', 'is_deleted')
        }),
        ('Additional Information', {
            'fields': ('created_at', 'updated_at'),
        })
    )
    list_display = ('id', 'name', 'price', 'category', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('category', 'is_deleted')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [ProductImageInline, ProductSKUInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_link', 'order_number', 'filename')
    list_display_links = ('product_link',)
    ordering = ('product__name', 'order_number')

    def product_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        product = obj.product
        if product:
            url = reverse('admin:products_product_change', args=[product.pk])
            return format_html('<a href="{}">{}</a>', url, product.name)
        return "-"
    product_link.short_description = 'Product'

@admin.register(ProductSKU)
class ProductSKUAdmin(admin.ModelAdmin):
    list_display = ('product_link', 'sku', 'stock', 'payment_option', 'supplier_discount')
    list_display_links = ('product_link',)
    ordering = ('product__name', 'sku')
    search_fields = ('sku', 'product__name')

    def product_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        product = obj.product
        if product:
            url = reverse('admin:products_product_change', args=[product.pk])
            return format_html('<a href="{}">{}</a>', url, product.name)
        return "-"
    product_link.short_description = 'Product'
