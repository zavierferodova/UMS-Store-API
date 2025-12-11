import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import IntegerField, Max, Value
from django.db.models.functions import Cast, StrIndex, Substr


class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True, blank=True)
    discount = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    sales = models.JSONField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            name = self.name.upper()
            words = [w for w in name.split() if w]

            alpha_part = "XXX"
            if len(words) == 1:
                alpha_part = words[0][:3].ljust(3, 'X')
            elif len(words) == 2:
                alpha_part = (words[0][0] + words[1][0] + 'X')
            elif len(words) >= 3:
                alpha_part = "".join(word[0] for word in words[:3])

            alpha_part = alpha_part.upper()

            max_num = Supplier.objects.filter(
                code__regex=r'^\d+\-'
            ).annotate(
                num_part=Cast(
                    Substr('code', 1, StrIndex('code', Value('-')) - 1),
                    output_field=IntegerField()
                )
            ).aggregate(
                max_num=Max('num_part')
            )['max_num'] or 0
            numeric_part = max_num + 1

            formatted_numeric_part = str(numeric_part).zfill(4)

            self.code = f"{formatted_numeric_part}-{alpha_part}"

        super().save(*args, **kwargs)
