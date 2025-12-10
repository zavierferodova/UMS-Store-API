from django.db import transaction
from rest_framework import serializers

from products.models.sku import ProductSKU
from users.serializers import UserSerializer

from .models import Transaction, TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(write_only=True)
    name = serializers.CharField(source='product_sku.product.name', read_only=True)
    sku_code = serializers.CharField(source='product_sku.sku', read_only=True)

    class Meta:
        model = TransactionItem
        fields = ['product_sku', 'name', 'sku_code', 'unit_price', 'amount']

    def validate_product_sku(self, value):
        if not ProductSKU.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product SKU does not exist.")
        return value

class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['pay', 'is_saved']

class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'code', 'cashier', 'pay', 'sub_total',
            'discount_total', 'total', 'payment', 'note',
            'is_saved', 'paid_time', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'sub_total', 'total', 'created_at', 'updated_at', 'paid_time']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['cashier'] = UserSerializer(instance.cashier).data
        return response

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        calculated_sub_total = 0
        items_to_create = []

        # Calculate sub_total and prepare items data
        for item_data in items_data:
            sku_code = item_data.pop('product_sku')
            product_sku_instance = ProductSKU.objects.select_related('product').get(sku=sku_code)
            price = item_data['unit_price']
            amount = item_data['amount']
            
            item_total = price * amount
            calculated_sub_total += item_total
            
            items_to_create.append({
                'product_sku': product_sku_instance,
                'unit_price': price,
                'amount': amount
            })
            
        validated_data['sub_total'] = calculated_sub_total
        
        # Calculate total (sub_total - discount_total)
        discount = validated_data.get('discount_total') or 0
        validated_data['total'] = max(0, calculated_sub_total - discount)
        
        with transaction.atomic():
            # Create transaction
            transaction_instance = Transaction.objects.create(**validated_data)
            
            # Create transaction items
            for item in items_to_create:
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    **item
                )
                
                # Optional: Update stock here if required by business logic
                # product_sku_instance = item['product_sku']
                # product_sku_instance.stock -= item['amount']
                # product_sku_instance.save()
                
        return transaction_instance
