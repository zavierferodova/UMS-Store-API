import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models.sku import ProductSKU
from purchase_orders.models.purchase_order import PurchaseOrder


class PoItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    product_sku = models.ForeignKey(ProductSKU, on_delete=models.PROTECT)
    price = models.BigIntegerField()
    amounts = models.IntegerField()
    supplier_discount = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'po_items'

    def __str__(self):
        return f"{self.amounts} of {self.product_sku.product.name} for {self.purchase_order}"
