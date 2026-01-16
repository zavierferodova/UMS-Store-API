from rest_framework import serializers

from products.models.sku import ProductSKU
from products.serializers.category import ProductCategorySerializer
from transactions.models.transaction_item import TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(write_only=True)
    name = serializers.CharField(source='product_sku.product.name', read_only=True)
    sku_code = serializers.CharField(source='product_sku.sku', read_only=True)

    class Meta:
        model = TransactionItem
        fields = ['product_sku', 'name', 'sku_code', 'unit_price', 'amount', 'supplier_discount']
        read_only_fields = ['unit_price']

    def validate_product_sku(self, value):
        if not ProductSKU.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product SKU does not exist.")
        return value


class SupplierTransactionItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='product_sku.product.id', read_only=True)
    name = serializers.CharField(source='product_sku.product.name', read_only=True)
    sku = serializers.CharField(source='product_sku.sku', read_only=True)
    category = ProductCategorySerializer(source='product_sku.product.category', read_only=True)
    transaction_id = serializers.UUIDField(source='transaction.id', read_only=True)
    transaction_code = serializers.CharField(source='transaction.code', read_only=True)
    purchase_date = serializers.DateTimeField(source='transaction.paid_time', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = TransactionItem
        fields = ['id', 'name', 'sku', 'category',  'transaction_id', 'transaction_code', 'unit_price', 'amount', 'total_price', 'purchase_date']

    def get_total_price(self, obj):
        return obj.unit_price * obj.amount
