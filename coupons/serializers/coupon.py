from rest_framework import serializers

from coupons.models.coupon import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError("End time cannot be before start time.")

        return data
