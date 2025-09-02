from rest_framework import serializers
from products.models.sku import ProductSKU

class ProductSKUNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSKU
        fields = ['sku', 'stock']
        read_only_fields = ['stock']

class ProductSKUStockUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSKU
        fields = ['sku', 'stock']
        read_only_fields = ['sku']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value