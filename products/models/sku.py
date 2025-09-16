from django.db import models

from products.models.base import BaseModel
from products.models.product import Product


class ProductSKU(BaseModel):
    """
    Represents a stock keeping unit (SKU) for a product.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")
    sku = models.CharField(max_length=12, unique=True, blank=False, null=False)
    stock = models.IntegerField(default=0, blank=False, null=False)

    class Meta:
        verbose_name = "Product SKU"
        verbose_name_plural = "Product SKUs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.sku
