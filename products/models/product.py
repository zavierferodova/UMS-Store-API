from products.models.base import BaseModel
from django.db import models
from products.models.category import ProductCategory

class Product(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField()
    price = models.BigIntegerField()
    additional_info = models.JSONField(null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.name