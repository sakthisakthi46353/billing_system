from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem

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
from django.shortcuts import render
from django.db.models import Sum, F
from customers.models import Customer
from invoices.models import InvoiceItem
from payments.models import Payment


def customer_balance(request):
    report_data = []

    customers = Customer.objects.all()

    for customer in customers:
        # Total invoiced amount
        invoice_total = InvoiceItem.objects.filter(
            invoice__customer=customer
        ).aggregate(
            total=Sum(F("quantity") * F("unit_price"))
        )["total"] or 0

        # Total paid amount
        paid_total = Payment.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        balance = invoice_total - paid_total

        # ✅ ONLY ONE APPEND (inside loop)
        report_data.append({
            "customer": customer,
            "invoice_total": invoice_total,
            "paid_total": paid_total,
            "balance": balance,
        })

    # ✅ return MUST be OUTSIDE for loop
    return render(request, "reports/customer_balance.html", {
        "report_data": report_data
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

    rows = []
    running_balance = 0

    # INVOICES
    invoices = Invoice.objects.filter(customer=customer).order_by("date")

    for inv in invoices:
        invoice_total = InvoiceItem.objects.filter(
            invoice=inv
        ).aggregate(
            total=Sum(F("quantity") * F("unit_price"))
        )["total"] or 0

        running_balance += invoice_total

        rows.append({
            "date": inv.date,
            "description": f"Invoice #{inv.id}",
            "debit": invoice_total,
            "credit": "",
            "balance": running_balance,
        })

    # PAYMENTS
    payments = Payment.objects.filter(customer=customer).order_by("date")

    for pay in payments:
        running_balance -= pay.amount

        rows.append({
            "date": pay.date,
            "description": "Payment",
            "debit": "",
            "credit": pay.amount,
            "balance": running_balance,
        })

    return render(request, "reports/customer_statement.html", {
        "customer": customer,
        "rows": rows,
    })
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, F

from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)

    # Invoice items
    items = InvoiceItem.objects.filter(invoice=invoice)

    # Subtotal (qty * unit_price)
    subtotal = items.aggregate(
        total=Sum(F("quantity") * F("unit_price"))
    )["total"] or 0

    # ✅ Payments are linked by CUSTOMER (NOT invoice)
    paid = Payment.objects.filter(
        customer=invoice.customer
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    balance = subtotal - paid

    return render(request, "invoices/invoice_pdf.html", {
        "invoice": invoice,
        "items": items,
        "subtotal": subtotal,
        "paid": paid,
        "balance": balance,
    })
