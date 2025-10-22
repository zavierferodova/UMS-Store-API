from rest_framework import serializers

from products.models.sku import ProductSKU
from products.serializers.product import ProductSerializer
from purchase_orders.models.po_item import PoItem
from purchase_orders.models.purchase_order import PurchaseOrder
from suppliers.models.supplier import Supplier
from suppliers.serializers.supplier import SupplierSerializer
from users.models import User
from users.serializers import UserSerializer


class PoItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField()
    product = ProductSerializer(source='product_sku.product', read_only=True)
    
    class Meta:
        model = PoItem
        fields = ('product_sku', 'product', 'price', 'amounts', 'remain_stock', 'supplier_discount')

    def validate_product_sku(self, value):
        try:
            return ProductSKU.objects.get(sku=value)
        except ProductSKU.DoesNotExist:
            raise serializers.ValidationError(f'Product SKU "{value}" does not exist.')
            
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_sku'] = instance.product_sku.sku if instance.product_sku else None
        return representation

class PurchaseOrderSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )
    supplier = SupplierSerializer(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'code',
            'user_id',
            'user',
            'supplier_id',
            'supplier',
            'payout',
            'completed',
            'is_deleted',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'code', 'is_deleted', 'created_at', 'updated_at')
