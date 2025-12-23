from django.db import models
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # ✅ IMPORTANT FIX
    opening_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    def __str__(self):
        return self.name
