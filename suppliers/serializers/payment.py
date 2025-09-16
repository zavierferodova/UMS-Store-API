from rest_framework import serializers

from suppliers.models.payment import SupplierPayment
from suppliers.models.supplier import Supplier


class SupplierPaymentSerializer(serializers.ModelSerializer):
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=False
    )

    class Meta:
        model = SupplierPayment
        fields = ['id', 'supplier_id', 'name', 'owner', 'account_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
