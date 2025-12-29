from rest_framework import serializers

from coupons.models.coupon import Coupon
from coupons.models.coupon_code import CouponCode


class CouponCodeSerializer(serializers.ModelSerializer):
    coupon_id = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.all(), source='coupon')

    class Meta:
        model = CouponCode
        fields = ['coupon_id', 'code', 'stock', 'used', 'disabled', 'created_at', 'updated_at']
        read_only_fields = ['used', 'created_at', 'updated_at']

    def validate_stock(self, value):
        if self.instance:
            if value < self.instance.used:
                raise serializers.ValidationError("Stock cannot be less than the number of times used.")
        return value
