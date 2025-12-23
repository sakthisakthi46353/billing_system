from django.db import models
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")   # ✅ IMPORTANT
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
