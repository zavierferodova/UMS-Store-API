from rest_framework import serializers
from coupons.models.coupon_code import CouponCode
from coupons.models.coupon import Coupon

class CouponCodeSerializer(serializers.ModelSerializer):
    coupon_id = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.all(), source='coupon')
    used = serializers.SerializerMethodField()

    class Meta:
        model = CouponCode
        fields = ['coupon_id', 'code', 'stock', 'used', 'disabled', 'created_at', 'updated_at']
        read_only_fields = ['used', 'created_at', 'updated_at']

    def get_used(self, obj):
        return obj.transactions.count()

    def validate_stock(self, value):
        if self.instance:
            used = self.instance.transactions.count()
            if value < used:
                raise serializers.ValidationError("Stock cannot be less than the number of times used.")
        return value
