from products.models.base import BaseModel
from django.db import models
from products.models.product import Product
from django.core.validators import FileExtensionValidator
import uuid
import os

def handle_upload_image(instance, filename):
    """
    Generates a unique filename for uploaded files using UUID.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('product_images/', filename)

class ProductImage(BaseModel):
    order_number = models.PositiveSmallIntegerField(default=0)
    filename = models.ImageField(
        upload_to=handle_upload_image,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pd_images'

    def __str__(self):
        return self.filename.name
