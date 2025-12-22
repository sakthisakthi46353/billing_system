from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    is_active = models.BooleanField(default=True)

    # 🔥 IMPORTANT: auto timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.name

    # =============================
    # CALCULATED FIELDS
    # =============================

    @property
    def total_purchase_amount(self):
        total = Decimal("0.00")
        for purchase in self.purchases.all():
            for item in purchase.items.all():
                total += (item.quantity * item.price)
        return total

    @property
    def total_paid_amount(self):
        return self.payments.aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]

    @property
    def balance_amount(self):
        return self.opening_balance + self.total_purchase_amount - self.total_paid_amount

    @property
    def payment_status(self):
        if self.balance_amount <= 0:
            return "PAID"
        elif self.total_paid_amount > 0:
            return "PARTIAL"
        return "UNPAID"
