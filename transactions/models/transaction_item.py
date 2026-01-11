import uuid

from django.db import models

from products.models.sku import ProductSKU
from transactions.models.transaction import Transaction


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
