from django.shortcuts import render
from django.db.models import Sum
from customers.models import Customer
from products.models import Product
from invoices.models import Invoice

def dashboard(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()

    total_revenue = Invoice.objects.aggregate(
        total=Sum("total")
    )["total"] or 0

    recent_invoices = (
        Invoice.objects
        .select_related("customer")
        .order_by("-id")[:5]
    )

    return render(request, "dashboard/dashboard.html", {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "recent_invoices": recent_invoices,
    })
