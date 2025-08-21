from enum import unique
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max

def generate_incremental_code():
    last_code = Supplier.objects.aggregate(max_code=Max('code'))['max_code']
    if last_code and last_code[1:].isdigit():
        new_number = int(last_code[1:]) + 1
    else:
        new_number = 1
    return 'S' + str(new_number).zfill(9)

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=10, default=generate_incremental_code, unique=True)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True, blank=True)
    discount = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
