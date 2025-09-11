from django.contrib import admin
from products.models.category import ProductCategory
from products.models.product import Product
from products.models.image import ProductImage
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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Base Information', {
            'fields': ('id', 'name', 'description', 'price', 'additional_info', 'category')
        }),
        ('Additional Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    list_display = ('id', 'name', 'category', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [ProductImageInline]

admin.site.register(ProductImage)
admin.site.register(ProductSKU)
