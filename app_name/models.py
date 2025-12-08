from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("UNPAID", "UNPAID"),
                 ("PARTIALLY_PAID", "PARTIALLY_PAID"),
                 ("PAID", "PAID")],
        default="UNPAID"
    )

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.invoiceitem_set.all())

    @property
    def tax(self):
        return self.subtotal * 0.05

    @property
    def grand_total(self):
        return self.subtotal + self.tax

    def __str__(self):
        return f"Invoice #{self.id}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    @property
    def total_price(self):
        return self.quantity * self.product.price


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Invoice {self.invoice.id}"
