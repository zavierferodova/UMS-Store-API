from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from cashier_books.models import CashierBook
from coupons.models.coupon_code import CouponCode
from products.models.sku import ProductSKU
from transactions.models import TransactionCashierBooks
from users.serializers import UserSerializer

from .models import Transaction, TransactionCoupon, TransactionItem


class TransactionCouponOutputSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='coupon_code.code')
    name = serializers.CharField(source='coupon_code.coupon.name')
    type = serializers.CharField(source='coupon_code.coupon.type')
    item_discount_percentage = serializers.CharField(source='coupon_code.coupon.discount_percentage', read_only=True)

    class Meta:
        model = TransactionCoupon
        fields = [
            'name', 'type', 'code', 'item_voucher_value', 'item_discount_percentage', 'item_discount_value', 'amount'
        ]


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

class TransactionUpdateSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True, required=False)
    coupons = TransactionCouponOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ['pay', 'is_saved', 'items', 'discount_total', 'payment', 'note', 'coupons']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        coupons_data = self.initial_data.get('coupons', None)
        
        with transaction.atomic():
            # Check payment status
            was_paid = instance.paid_time is not None
            is_becoming_paid = validated_data.get('paid_time') is not None
            is_paid_now = was_paid or is_becoming_paid

            if items_data is not None:
                # 1. Retrieve all of old items from database
                old_items = {item.product_sku.sku: item for item in instance.items.select_related('product_sku__product').all()}
                new_items_skus = set(item['product_sku'] for item in items_data)
                
                # 2. If the item is not inputed on new payload delete it, and append stock to related product sku item.
                for sku, old_item in old_items.items():
                    if sku not in new_items_skus:
                        if was_paid:
                            old_item.product_sku.stock += old_item.amount
                            old_item.product_sku.save()
                        old_item.delete()
                
                # 3. If the item not exists on old items, add new and negative stock based on amounts that inputed.
                for item_data in items_data:
                    sku_code = item_data['product_sku']
                    amount = item_data['amount']
                    
                    if sku_code in old_items:
                        old_item = old_items[sku_code]
                        # Update existing item
                        if is_paid_now:
                            if was_paid:
                                stock_diff = amount - old_item.amount
                                if stock_diff != 0:
                                    old_item.product_sku.stock -= stock_diff
                                    old_item.product_sku.save()
                            else:
                                old_item.product_sku.stock -= amount
                                old_item.product_sku.save()
                        
                        old_item.amount = amount
                        old_item.unit_price = old_item.product_sku.product.price
                        old_item.save()
                    else:
                        # Add new item
                        product_sku_instance = ProductSKU.objects.select_related('product').get(sku=sku_code)
                        TransactionItem.objects.create(
                            transaction=instance,
                            product_sku=product_sku_instance,
                            unit_price=product_sku_instance.product.price,
                            amount=amount
                        )
                        if is_paid_now:
                            product_sku_instance.stock -= amount
                            product_sku_instance.save()
            
            elif is_becoming_paid and not was_paid:
                for item in instance.items.select_related('product_sku').all():
                    item.product_sku.stock -= item.amount
                    item.product_sku.save()
            
            if coupons_data is not None:
                old_coupons = {c.coupon_code.code: c for c in instance.coupons.select_related('coupon_code').all()}
                new_coupons_codes = set(c.get('code') for c in coupons_data)
                
                # Delete removed coupons
                for code, old_coupon in old_coupons.items():
                    if code not in new_coupons_codes:
                        old_coupon.coupon_code.used -= old_coupon.amount
                        old_coupon.coupon_code.save()
                        old_coupon.delete()
                
                # Add/Update coupons
                for coupon_data in coupons_data:
                    code = coupon_data.get('code')
                    amount = coupon_data.get('amount')
                    
                    if code in old_coupons:
                        old_coupon = old_coupons[code]
                        diff = amount - old_coupon.amount
                        if diff != 0:
                            if diff > 0:
                                if old_coupon.coupon_code.stock < (old_coupon.coupon_code.used + diff):
                                     raise serializers.ValidationError(f"Coupon {code} out of stock.")
                            
                            old_coupon.coupon_code.used += diff
                            old_coupon.coupon_code.save()
                            old_coupon.amount = amount
                            old_coupon.save()
                    else:
                        try:
                            coupon_code_instance = CouponCode.objects.get(code=code)
                            if coupon_code_instance.disabled:
                                raise serializers.ValidationError(f"Coupon {code} is disabled.")
                            if coupon_code_instance.stock < (coupon_code_instance.used + amount):
                                raise serializers.ValidationError(f"Coupon {code} out of stock.")
                            
                            now = timezone.now()
                            if coupon_code_instance.coupon.start_time > now or coupon_code_instance.coupon.end_time < now:
                                raise serializers.ValidationError(f"Coupon {code} is not valid at this time.")

                            TransactionCoupon.objects.create(
                                transaction=instance,
                                coupon_code=coupon_code_instance,
                                amount=amount
                            )
                            coupon_code_instance.used += amount
                            coupon_code_instance.save()
                        except CouponCode.DoesNotExist:
                             raise serializers.ValidationError(f"Coupon code {code} not found.")
            
            # Update other fields
            instance = super().update(instance, validated_data)
            
            # Recalculate totals if items changed or coupons changed
            if items_data is not None or coupons_data is not None:
                if items_data is not None:
                    current_items = instance.items.all()
                    sub_total = sum(item.unit_price * item.amount for item in current_items)
                    instance.sub_total = sub_total
                else:
                    sub_total = instance.sub_total
                
                # Calculate discount from current coupons in DB
                current_coupons = instance.coupons.select_related('coupon_code__coupon').all()
                voucher_discount = 0
                percentage_discount = 0
                percentage_coupon_count = 0

                for transaction_coupon in current_coupons:
                    coupon = transaction_coupon.coupon_code.coupon
                    amount = transaction_coupon.amount
                    
                    item_voucher_value = None
                    item_discount_value = None

                    if coupon.type == 'discount':
                        percentage_coupon_count += 1
                        if percentage_coupon_count > 1:
                            raise serializers.ValidationError("Only one percentage discount coupon is allowed.")
                        if amount > 1:
                            raise serializers.ValidationError("Percentage discount coupon amount cannot be more than 1.")
                        
                        discount_amount = int(sub_total * coupon.discount_percentage / 100)
                        percentage_discount += discount_amount
                        item_discount_value = discount_amount
                        
                    elif coupon.type == 'voucher':
                        voucher_discount += (coupon.voucher_value * amount)
                        item_voucher_value = coupon.voucher_value
                    
                    transaction_coupon.item_voucher_value = item_voucher_value
                    transaction_coupon.item_discount_value = item_discount_value
                    transaction_coupon.save()
                
                instance.discount_total = int(voucher_discount + percentage_discount)
                instance.total = max(0, sub_total - instance.discount_total)
                instance.save()
            
            if instance.pay and instance.pay != 0:
                if instance.pay < instance.total:
                     print("CALLED")
                     print(instance.pay)
                     print(instance.total)
                     raise serializers.ValidationError({"pay": "Pay amount cannot be less than total amount."})
                     
        return instance

class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)
    coupons = TransactionCouponOutputSerializer(many=True, read_only=True)
    cashier_book_id = serializers.UUIDField(write_only=True)
    cashier = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'code', 'cashier', 'pay', 'sub_total',
            'discount_total', 'total', 'payment', 'note',
            'is_saved', 'paid_time', 'created_at', 'updated_at', 'items', 'coupons',
            'cashier_book_id'
        ]
        read_only_fields = ['id', 'sub_total', 'total', 'created_at', 'updated_at', 'paid_time']

    def get_cashier(self, obj):
        cbt = obj.cashier_book_transactions.select_related('cashier_book__cashier').first()
        if cbt:
            return UserSerializer(cbt.cashier_book.cashier).data
        return None

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        cashier_book_id = validated_data.pop('cashier_book_id')
        coupons_data = self.initial_data.get('coupons', [])
        
        try:
            cashier_book = CashierBook.objects.get(id=cashier_book_id)
        except CashierBook.DoesNotExist:
            raise serializers.ValidationError({"cashier_book_id": "Cashier book not found."})
        
        calculated_sub_total = 0
        items_to_create = []

        # Calculate sub_total and prepare items data
        for item_data in items_data:
            sku_code = item_data.pop('product_sku')
            product_sku_instance = ProductSKU.objects.select_related('product').get(sku=sku_code)
            price = product_sku_instance.product.price
            amount = item_data['amount']
            
            item_total = price * amount
            calculated_sub_total += item_total
            
            items_to_create.append({
                'product_sku': product_sku_instance,
                'unit_price': price,
                'amount': amount
            })
            
        validated_data['sub_total'] = calculated_sub_total
        
        # Validate coupons and calculate discount
        voucher_discount = 0
        percentage_discount = 0
        percentage_coupon_count = 0
        
        valid_coupons = []
        for coupon_data in coupons_data:
            code = coupon_data.get('code')
            amount = coupon_data.get('amount')
            try:
                coupon_code_instance = CouponCode.objects.select_related('coupon').get(code=code)
                if coupon_code_instance.disabled:
                     raise serializers.ValidationError(f"Coupon {code} is disabled.")
                if coupon_code_instance.stock < (coupon_code_instance.used + amount):
                     raise serializers.ValidationError(f"Coupon {code} out of stock.")
                
                now = timezone.now()
                if coupon_code_instance.coupon.start_time > now or coupon_code_instance.coupon.end_time < now:
                     raise serializers.ValidationError(f"Coupon {code} is not valid at this time.")
                
                item_voucher_value = None
                item_discount_value = None

                if coupon_code_instance.coupon.type == 'discount':
                    percentage_coupon_count += 1
                    if percentage_coupon_count > 1:
                        raise serializers.ValidationError("Only one percentage discount coupon is allowed.")
                    if amount > 1:
                        raise serializers.ValidationError("Percentage discount coupon amount cannot be more than 1.")
                    
                    discount_amount = int(calculated_sub_total * coupon_code_instance.coupon.discount_percentage / 100)
                    percentage_discount += discount_amount
                    item_discount_value = discount_amount
                elif coupon_code_instance.coupon.type == 'voucher':
                    voucher_discount += (coupon_code_instance.coupon.voucher_value * amount)
                    item_voucher_value = coupon_code_instance.coupon.voucher_value

                valid_coupons.append({
                    'coupon_code': coupon_code_instance,
                    'amount': amount,
                    'item_voucher_value': item_voucher_value,
                    'item_discount_value': item_discount_value
                })
            except CouponCode.DoesNotExist:
                raise serializers.ValidationError(f"Coupon code {code} not found.")

        total_discount = int(voucher_discount + percentage_discount)
        validated_data['discount_total'] = total_discount
        validated_data['total'] = max(0, calculated_sub_total - total_discount)

        pay = validated_data.get('pay')
        if pay and pay < validated_data['total']:
             raise serializers.ValidationError({"pay": "Pay amount cannot be less than total amount."})

        with transaction.atomic():
            # Create transaction
            transaction_instance = Transaction.objects.create(**validated_data)
            
            TransactionCashierBooks.objects.create(
                cashier_book=cashier_book,
                transaction=transaction_instance
            )

            # Create transaction items
            for item in items_to_create:
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    **item
                )
                
                if transaction_instance.paid_time:
                    product_sku_instance = item['product_sku']
                    product_sku_instance.stock -= item['amount']
                    product_sku_instance.save()
            
            # Create transaction coupons
            for coupon_item in valid_coupons:
                TransactionCoupon.objects.create(
                    transaction=transaction_instance,
                    coupon_code=coupon_item['coupon_code'],
                    amount=coupon_item['amount'],
                    item_voucher_value=coupon_item['item_voucher_value'],
                    item_discount_value=coupon_item['item_discount_value']
                )
                coupon_item['coupon_code'].used += coupon_item['amount']
                coupon_item['coupon_code'].save()
                
        return transaction_instance
