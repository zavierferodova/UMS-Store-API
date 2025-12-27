import uuid
from django.db import models

class Coupon(models.Model):
    TYPE_CHOICES = [
        ('voucher', 'Fixed'),
        ('discount', 'Percentage'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    voucher_value = models.BigIntegerField(null=True, blank=True)
    discount_percentage = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupons'

    def __str__(self):
        return self.name