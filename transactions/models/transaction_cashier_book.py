import uuid

from django.db import models

from cashier_books.models import CashierBook
from transactions.models.transaction import Transaction


class TransactionCashierBooks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cashier_book = models.ForeignKey(CashierBook, on_delete=models.CASCADE, related_name='transactions')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='cashier_book_transactions')

    class Meta:
        db_table = 'transaction_cashier_books'

    def __str__(self):
        return f"{self.transaction} - {self.cashier_book_id}"
