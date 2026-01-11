from rest_framework import serializers

from products.models.sku import ProductSKU
from transactions.models.transaction_item import TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(write_only=True)
    name = serializers.CharField(source='product_sku.product.name', read_only=True)
    sku_code = serializers.CharField(source='product_sku.sku', read_only=True)

    class Meta:
        model = TransactionItem
        fields = ['product_sku', 'name', 'sku_code', 'unit_price', 'amount']
        read_only_fields = ['unit_price']

    def validate_product_sku(self, value):
        if not ProductSKU.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product SKU does not exist.")
        return value
