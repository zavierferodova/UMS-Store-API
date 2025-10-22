import os
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

from products.models.product import Product


def handle_upload_image(instance, filename):
    """
    Generates a unique filename for uploaded files using UUID.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('product_images/', filename)

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.PositiveSmallIntegerField(default=0)
    filename = models.ImageField(
        upload_to=handle_upload_image,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'pd_images'

    def __str__(self):
        return self.filename.name
