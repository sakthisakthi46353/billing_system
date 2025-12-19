from django.db import models
from decimal import Decimal
from customers.models import Customer
from products.models import Product


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UNPAID'
    )

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

    # ----------------------
    # Total paid amount
    # ----------------------
    @property
    def paid_amount(self):
        return sum(
            (payment.amount for payment in self.payments.all()),
            Decimal('0.00')
        )

    # ----------------------
    # Remaining balance
    # ----------------------
    @property
    def balance(self):
        return self.total - self.paid_amount

    # ----------------------
    # Update invoice status
    # ----------------------
    def update_status(self):
        if self.paid_amount <= 0:
            self.status = 'UNPAID'
        elif self.paid_amount < self.total:
            self.status = 'PARTIALLY_PAID'
        else:
            self.status = 'PAID'
        self.save()


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # ----------------------
    # Line total (price × qty)
    # ----------------------
    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
