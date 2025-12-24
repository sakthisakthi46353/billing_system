from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, F

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


@login_required
def dashboard(request):
    # ✅ Counts
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()

    # ✅ Total Revenue (from InvoiceItem)
    total_revenue = InvoiceItem.objects.aggregate(
        total=Sum(F("quantity") * F("unit_price"))
    )["total"] or 0

    # ✅ Recent Invoices
    recent_invoices = Invoice.objects.select_related(
        "customer"
    ).order_by("-id")[:5]

    return render(request, "dashboard/dashboard.html", {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "recent_invoices": recent_invoices,
    })
