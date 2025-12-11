import uuid

from django.db import models

from products.models.product import Product


class ProductSKU(models.Model):
    """
    Represents a stock keeping unit (SKU) for a product.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")
    sku = models.CharField(max_length=12, unique=True, blank=False, null=False)
    stock = models.IntegerField(default=0, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_skus"
        ordering = ["-created_at"]

    def __str__(self):
        return f"({self.sku}) {self.product.name}"
