from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    discount = serializers.IntegerField(min_value=0, max_value=100)
    sales = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True,
        help_text='List of sales with name and phone. Format: [{"name": "string", "phone": "string"}]'
    )

    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'address', 'phone', 'email', 'discount', 'sales', 'is_deleted', 'created_at', 'updated_at']

    def validate_sales(self, value):
        if value is None:
            return value
            
        if not isinstance(value, list):
            raise serializers.ValidationError('Sales must be a list of objects')
            
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Each sale item must be an object')
                
            if 'name' not in item or 'phone' not in item:
                raise serializers.ValidationError('Each sale item must have "name" and "phone" fields')
                
            if not isinstance(item['name'], str) or not isinstance(item['phone'], str):
                raise serializers.ValidationError('Both "name" and "phone" must be strings')
                
        return value
