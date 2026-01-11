from rest_framework import serializers

from transactions.models.transaction_coupon import TransactionCoupon


class TransactionCouponOutputSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='coupon_code.code')
    name = serializers.CharField(source='coupon_code.coupon.name')
    type = serializers.CharField(source='coupon_code.coupon.type')
    item_discount_percentage = serializers.IntegerField(source='coupon_code.coupon.discount_percentage', read_only=True)

    class Meta:
        model = TransactionCoupon
        fields = [
            'name', 'type', 'code', 'item_voucher_value', 'item_discount_percentage', 'item_discount_value', 'amount'
        ]
