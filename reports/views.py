from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F

from customers.models import Customer
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


# =========================
# REPORTS HOME PAGE
# =========================
from django.shortcuts import render

def reports_home(request):
    return render(request, "reports/home.html")


# =========================
# CUSTOMER BALANCE SUMMARY
# =========================
from django.shortcuts import render
from django.db.models import Sum, F
from customers.models import Customer
from invoices.models import InvoiceItem
from payments.models import Payment

def customer_balance(request):
    report_data = []

    customers = Customer.objects.all()

    for customer in customers:
        # ✅ Total Invoiced
        total_invoiced = InvoiceItem.objects.filter(
            invoice__customer=customer
        ).aggregate(
            total=Sum(F('unit_price') * F('quantity'))
        )['total'] or 0

        # ✅ Total Paid (FIXED)
        total_paid = Payment.objects.filter(
            customer=customer
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        balance = total_invoiced - total_paid

        report_data.append({
            'customer': customer,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance': balance
        })

    return render(request, 'reports/customer_balance.html', {
        'report_data': report_data
    })


# =========================
# SALES SUMMARY REPORT
# =========================
from django.db.models import Sum, F
from invoices.models import InvoiceItem

def sales_summary(request):
    sales = (
        InvoiceItem.objects
        .values('invoice__date')
        .annotate(total_sales=Sum(F('unit_price') * F('quantity')))
        .order_by('invoice__date')
    )

    grand_total = (
        InvoiceItem.objects.aggregate(
            total=Sum(F('unit_price') * F('quantity'))
        )['total'] or 0
    )

    return render(request, 'reports/sales_summary.html', {
        'sales': sales,
        'grand_total': grand_total
    })


# =========================
# TOP SELLING PRODUCTS
# =========================
from django.shortcuts import render
from django.db.models import Sum, F
from invoices.models import InvoiceItem

def top_products(request):
    products = (
        InvoiceItem.objects
        .values('product__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_sales=Sum(F('unit_price') * F('quantity'))
        )
        .order_by('-total_qty')
    )

    return render(request, 'reports/top_products.html', {
        'products': products
    })


# =========================
# CUSTOMER STATEMENT - SELECT CUSTOMER
# =========================
def customer_statement_select(request):
    customers = Customer.objects.all()
    return render(request, 'reports/customer_statement_select.html', {
        'customers': customers
    })


# =========================
# CUSTOMER STATEMENT - FINAL
# =========================
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F
from customers.models import Customer
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment

def customer_statement(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # 🔹 Invoices for this customer
    invoices = Invoice.objects.filter(customer=customer).order_by('date')

    # 🔹 Payments for this customer (FIXED)
    payments = Payment.objects.filter(customer=customer).order_by('date')

    # 🔹 Invoice total
    total_invoiced = InvoiceItem.objects.filter(
        invoice__customer=customer
    ).aggregate(
        total=Sum(F('unit_price') * F('quantity'))
    )['total'] or 0

    # 🔹 Payment total
    total_paid = payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    balance = total_invoiced - total_paid

    return render(request, 'reports/customer_statement.html', {
        'customer': customer,
        'invoices': invoices,
        'payments': payments,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance': balance
    })
