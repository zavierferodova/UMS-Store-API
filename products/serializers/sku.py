from rest_framework import serializers

from products.models.product import Product
from products.models.sku import ProductSKU


class ProductSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSKU
        fields = ['id', 'sku', 'stock']
        read_only_fields = ['id']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

class ProductSKUCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product'
    )

    class Meta:
        model = ProductSKU
        fields = ['id', 'sku', 'stock', 'product_id']
        read_only_fields = ['id']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value
