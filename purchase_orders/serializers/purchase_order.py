from rest_framework import serializers
from purchase_orders.models.purchase_order import PurchaseOrder
from suppliers.models.supplier import Supplier
from suppliers.serializers.supplier import SupplierSerializer
from users.models import User
from users.serializers import UserSerializer

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
            'draft',
            'completed',
            'is_deleted',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'code', 'is_deleted', 'created_at', 'updated_at')
