import uuid
from datetime import datetime

from django.db import models

from suppliers.models.supplier import Supplier
from users.models import User


class PurchaseOrder(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        PARTNERSHIP = "partnership", "Partnership"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    payout = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    draft = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    note = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"PO-{datetime.now().strftime('%Y%m%d')}-{self.id.hex[:4]}"
        super().save(*args, **kwargs)
