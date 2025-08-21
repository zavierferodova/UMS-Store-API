from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    discount = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'address', 'phone', 'email', 'discount', 'is_deleted', 'created_at', 'updated_at']
