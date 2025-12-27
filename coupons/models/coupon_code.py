import uuid

from django.db import models

from .coupon import Coupon


class CouponCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='codes')
    code = models.CharField(max_length=64, unique=True)
    stock = models.IntegerField()
    used = models.IntegerField(default=0)
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupon_code'

    def __str__(self):
        return self.code
