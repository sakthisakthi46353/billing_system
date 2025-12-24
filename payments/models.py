from django.db import models
from customers.models import Customer

class Payment(models.Model):

    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Card'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='CASH'
    )

    def __str__(self):
        return f"{self.customer.name} - {self.amount} ({self.method})"
