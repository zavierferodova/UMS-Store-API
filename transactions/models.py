import uuid
from datetime import datetime

from django.db import models

from products.models.sku import ProductSKU
from users.models import User


class Transaction(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('cashless', 'Cashless'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, editable=False, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactions')
    pay = models.BigIntegerField(null=True, blank=True)
    sub_total = models.BigIntegerField()
    discount_total = models.BigIntegerField(null=True, blank=True)
    total = models.BigIntegerField()
    payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES, null=True, blank=True)
    note = models.CharField(null=True, blank=True, max_length=255)
    is_saved = models.BooleanField(default=False)
    paid_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'

    def __str__(self):
        return f"{self.id}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"TRANS/{datetime.now().strftime('%Y%m%d')}/{self.id.hex[:4]}"
        super().save(*args, **kwargs)

class TransactionItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_sku = models.ForeignKey(ProductSKU, on_delete=models.PROTECT, related_name='transaction_items')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    unit_price = models.BigIntegerField()
    amount = models.IntegerField()

    class Meta:
        db_table = 'transaction_item'

    def __str__(self):
        return f"{self.product_sku} - {self.transaction}"
