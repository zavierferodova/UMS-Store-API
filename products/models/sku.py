import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models.product import Product
from purchase_orders.models.purchase_order import PurchaseOrderPaymentOption
from suppliers.models.supplier import Supplier


class ProductSKU(models.Model):
    """
    Represents a stock keeping unit (SKU) for a product.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="skus")
    sku = models.CharField(max_length=12, unique=True, blank=False, null=False)
    stock = models.IntegerField(default=0, blank=False, null=False)
    payment_option = models.CharField(
        max_length=20,
        choices=PurchaseOrderPaymentOption.choices,
        blank=True,
        null=True,
    )
    partnership_discount = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_skus"
        ordering = ["-created_at"]

    def __str__(self):
        return f"({self.sku}) {self.product.name}"
