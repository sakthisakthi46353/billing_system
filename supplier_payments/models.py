from django.db import models
from suppliers.models import Supplier

class SupplierPayment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Card'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField()  # 👈 manual date
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.supplier.name} - {self.amount}"
