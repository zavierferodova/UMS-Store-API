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
    items = TransactionItemSerializer(many=True, required=False)

    class Meta:
        model = Transaction
        fields = ['pay', 'is_saved', 'items', 'discount_total', 'payment', 'note']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        with transaction.atomic():
            if items_data is not None:
                # 1. Retrieve all of old items from database
                old_items = {item.product_sku.sku: item for item in instance.items.select_related('product_sku').all()}
                new_items_skus = set(item['product_sku'] for item in items_data)
                
                # 2. If the item is not inputed on new payload delete it, and append stock to related product sku item.
                for sku, old_item in old_items.items():
                    if sku not in new_items_skus:
                        old_item.product_sku.stock += old_item.amount
                        old_item.product_sku.save()
                        old_item.delete()
                
                # 3. If the item not exists on old items, add new and negative stock based on amounts that inputed.
                for item_data in items_data:
                    sku_code = item_data['product_sku']
                    amount = item_data['amount']
                    unit_price = item_data['unit_price']
                    
                    if sku_code in old_items:
                        old_item = old_items[sku_code]
                        # Update existing item
                        stock_diff = amount - old_item.amount
                        if stock_diff != 0:
                            old_item.product_sku.stock -= stock_diff
                            old_item.product_sku.save()
                        
                        old_item.amount = amount
                        old_item.unit_price = unit_price
                        old_item.save()
                    else:
                        # Add new item
                        product_sku_instance = ProductSKU.objects.get(sku=sku_code)
                        TransactionItem.objects.create(
                            transaction=instance,
                            product_sku=product_sku_instance,
                            unit_price=unit_price,
                            amount=amount
                        )
                        product_sku_instance.stock -= amount
                        product_sku_instance.save()
            
            # Update other fields
            instance = super().update(instance, validated_data)
            
            # Recalculate totals if items changed or discount_total changed
            if items_data is not None or 'discount_total' in validated_data:
                if items_data is not None:
                    current_items = instance.items.all()
                    sub_total = sum(item.unit_price * item.amount for item in current_items)
                    instance.sub_total = sub_total
                else:
                    sub_total = instance.sub_total
                
                discount_total = instance.discount_total or 0
                instance.total = max(0, sub_total - discount_total)
                instance.save()
            
            if instance.pay and instance.pay != 0:
                if instance.pay < instance.total:
                     raise serializers.ValidationError({"pay": "Pay amount cannot be less than total amount."})
                     
        return instance

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
                
                product_sku_instance = item['product_sku']
                product_sku_instance.stock -= item['amount']
                product_sku_instance.save()
                
        return transaction_instance
