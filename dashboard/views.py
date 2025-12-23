from django.shortcuts import render
from django.db.models import Sum

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice
from payments.models import Payment


def dashboard(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()

    # ✅ Total revenue = sum of payments
    total_revenue = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    recent_invoices = Invoice.objects.select_related(
        "customer"
    ).order_by("-id")[:5]

    context = {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "recent_invoices": recent_invoices,
    }

    return render(request, "dashboard/dashboard.html", context)
