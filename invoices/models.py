from django.db import models
from decimal import Decimal
from customers.models import Customer
from products.models import Product


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("UNPAID", "Unpaid"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="UNPAID"
    )

    def __str__(self):
        return f"Invoice #{self.id}"

    # ✅ ADD THIS (VERY IMPORTANT)
    @property
    def total(self):
        """
        Sum of all invoice item line totals
        """
        total = Decimal("0.00")

        for item in self.items.all():
            total += item.line_total

        return total


class InvoiceItem(models.Model):
    DISCOUNT_CHOICES = [
        ("percent", "%"),
        ("amount", "₹"),
    ]

    invoice = models.ForeignKey(
        Invoice, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )

    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_CHOICES, default="percent"
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    @property
    def line_total(self):
        """
        unit_price × qty − discount + tax
        """
        base = self.unit_price * self.quantity

        if self.discount_type == "percent":
            discount = base * (self.discount_value / Decimal("100"))
        else:
            discount = self.discount_value

        taxable = base - discount
        tax = taxable * (self.tax_percent / Decimal("100"))

        return taxable + tax
