from django.utils import timezone
from rest_framework import serializers

from coupons.models.coupon import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        now = timezone.now()

        if start_time and start_time < now:
            raise serializers.ValidationError("Start time cannot be in the past.")

        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError("End time cannot be before start time.")

        return data
