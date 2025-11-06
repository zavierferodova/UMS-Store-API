
from rest_framework import serializers

from purchase_orders.models.purchase_order import PurchaseOrder
from purchase_orders.serializers.po_item import NestedPoItemSerializer, PoItemSerializer
from suppliers.models.supplier import Supplier
from suppliers.serializers.supplier import SupplierSerializer
from users.models import User
from users.serializers import UserSerializer


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = NestedPoItemSerializer(many=True, required=False, write_only=True)
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
            'note',
            'draft',
            'completed',
            'is_deleted',
            'created_at',
            'updated_at',
            'items',
        )
        read_only_fields = ('id', 'code', 'is_deleted', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['items'] = PoItemSerializer(instance.items.all(), many=True).data
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase_order = super().create(validated_data)
        
        for item_data in items_data:
            item_data['purchase_order'] = purchase_order
            NestedPoItemSerializer().create(item_data)
        
        return purchase_order
