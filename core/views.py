from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


# ============================
# MAIN DASHBOARD (HOME PAGE)
# ============================
def dashboard(request):
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_invoices = Invoice.objects.count()

    # Total revenue from invoice items
    total_revenue = Decimal("0.00")
    for item in InvoiceItem.objects.all():
        total_revenue += item.line_total

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


# ============================
# CORE HOME (OPTIONAL)
# ============================
def core_home(request):
    return render(request, "core/core_home.html")


# ============================
# REPORTS HOME
# ============================
def reports_home(request):
    return render(request, "reports/home.html")


# ============================
# CUSTOMER BALANCE SUMMARY
# ============================
def customer_balance(request):
    report_data = []   # 🔴 NAME MUST MATCH TEMPLATE

    customers = Customer.objects.all()

    for c in customers:
        # Total invoiced
        total_invoiced = Decimal("0.00")
        items = InvoiceItem.objects.filter(
            invoice__customer=c
        )
        for item in items:
            total_invoiced += item.line_total

        # Total paid
        total_paid = Payment.objects.filter(
            invoice__customer=c
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        report_data.append({
            "customer": c,
            "total_invoice": total_invoiced,
            "total_paid": total_paid,
            "balance": total_invoiced - total_paid,
        })

    return render(request, "reports/customer_balance.html", {
        "report_data": report_data   # 🔴 SAME NAME
    })


# ============================
# SALES SUMMARY
# ============================
def sales_summary(request):
    total_invoices = Invoice.objects.count()

    total_sales = Decimal("0.00")
    for item in InvoiceItem.objects.all():
        total_sales += item.line_total

    total_payments = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    avg_invoice = (
        total_sales / total_invoices
        if total_invoices else Decimal("0.00")
    )

    return render(request, "reports/sales_summary.html", {
        "total_invoices": total_invoices,
        "total_sales": total_sales,
        "total_payments": total_payments,
        "avg_invoice": avg_invoice,
    })


# ============================
# TOP SELLING PRODUCTS
# ============================
def top_products(request):
    items = InvoiceItem.objects.values(
        "product__name"
    ).annotate(
        total_qty=Sum("quantity"),
        total_revenue=Sum(
            F("unit_price") * F("quantity")
        )
    ).order_by("-total_qty")

    return render(request, "reports/top_products.html", {
        "items": items
    })


# ============================
# CUSTOMER STATEMENT (SELECT)
# ============================
def customer_statement_select(request):
    customers = Customer.objects.all()
    return render(request, "reports/customer_statement_select.html", {
        "customers": customers
    })


# ============================
# CUSTOMER STATEMENT (DETAIL)
# ============================
def customer_statement(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = []

    invoices = Invoice.objects.filter(customer=customer)
    for inv in invoices:
        inv_total = Decimal("0.00")
        for item in inv.items.all():
            inv_total += item.line_total

        entries.append({
            "date": inv.date,
            "desc": f"Invoice #{inv.id}",
            "debit": inv_total,
            "credit": None,
        })

    payments = Payment.objects.filter(invoice__customer=customer)
    for pay in payments:
        entries.append({
            "date": pay.date.date(),
            "desc": "Payment",
            "debit": None,
            "credit": pay.amount,
        })

    # Sort by date
    entries.sort(key=lambda x: x["date"])

    balance = Decimal("0.00")
    for e in entries:
        if e["debit"]:
            balance += e["debit"]
        if e["credit"]:
            balance -= e["credit"]
        e["balance"] = balance

    return render(request, "reports/customer_statement.html", {
        "customer": customer,
        "entries": entries
    })
