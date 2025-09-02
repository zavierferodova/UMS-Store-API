from products.models.base import BaseModel
from django.db import models

class ProductCategory(BaseModel):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'pd_category'
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name