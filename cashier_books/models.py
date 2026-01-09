import uuid
from datetime import datetime

from django.db import models

from users.models import User


class CashierBook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cashier_books')
    cash_drawer = models.BigIntegerField()
    time_open = models.DateTimeField(auto_now_add=True)
    time_closed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cashier_books'

    def __str__(self):
        return f"{self.cashier} - {self.time_open}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"C-BOOK/{datetime.now().strftime('%Y%m%d')}/{self.id.hex[:4]}"
        super().save(*args, **kwargs)
