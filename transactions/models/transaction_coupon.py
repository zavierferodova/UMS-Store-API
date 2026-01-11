import uuid

from django.db import models

from coupons.models.coupon_code import CouponCode
from transactions.models.transaction import Transaction


class TransactionCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='coupons')
    coupon_code = models.ForeignKey(CouponCode, on_delete=models.CASCADE, related_name='transactions')
    item_discount_value = models.BigIntegerField(null=True, blank=True)
    item_voucher_value = models.BigIntegerField(null=True, blank=True)
    amount = models.IntegerField(default=1)

    class Meta:
        db_table = 'transaction_coupons'

    def __str__(self):
        return f"{self.coupon_code} - {self.transaction}"
