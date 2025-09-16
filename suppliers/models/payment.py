import uuid

from django.db import models

from suppliers.models.supplier import Supplier


class SupplierPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    name = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    account_number = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
