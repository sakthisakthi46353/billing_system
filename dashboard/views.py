from django.shortcuts import render
from customers.models import Customer
from products.models import Product
from invoices.models import Invoice
from payments.models import Payment

def dashboard(request):
    customers = Customer.objects.all()
    products = Product.objects.all()
    invoices = Invoice.objects.all().order_by('-id')
    payments = Payment.objects.all().order_by('-id')

    return render(request, 'dashboard/dashboard.html', {
        'customers': customers,
        'products': products,
        'invoices': invoices,
        'payments': payments,
    })
