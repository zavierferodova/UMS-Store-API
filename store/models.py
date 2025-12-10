from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
# Create your models here.
