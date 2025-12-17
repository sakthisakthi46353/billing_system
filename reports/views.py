from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F
from datetime import date

from customers.models import Customer
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


# =========================
# REPORTS HOME PAGE
# =========================
def reports_home(request):
    return render(request, 'reports/home.html')


# =========================
# CUSTOMER BALANCE SUMMARY
# =========================
def customer_balance_report(request):
    report_data = []

    customers = Customer.objects.all()

    for customer in customers:
        invoice_total = Invoice.objects.filter(
            customer=customer
        ).aggregate(total=Sum('total'))['total'] or 0

        paid_total = Payment.objects.filter(
            invoice__customer=customer
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = invoice_total - paid_total

        report_data.append({
            'customer': customer,
            'invoice_total': invoice_total,
            'paid_total': paid_total,
            'balance': balance
        })

    return render(request, 'reports/customer_balance.html', {
        'report': report_data
    })


# =========================
# SALES SUMMARY REPORT
# =========================
def sales_summary_report(request):
    total_invoices = Invoice.objects.count()

    total_sales = Invoice.objects.aggregate(
        total=Sum('total')
    )['total'] or 0

    total_tax = Invoice.objects.aggregate(
        total=Sum('tax')
    )['total'] or 0

    return render(request, 'reports/sales_summary.html', {
        'total_invoices': total_invoices,
        'total_sales': total_sales,
        'total_tax': total_tax
    })


# =========================
# TOP SELLING PRODUCTS
# =========================
def top_selling_products(request):
    products = (
        InvoiceItem.objects
        .values('product__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        )
        .order_by('-total_qty')
    )

    return render(request, 'reports/top_products.html', {
        'products': products
    })


# =========================
# CUSTOMER STATEMENT - SELECT
# =========================
def customer_statement_select(request):
    customers = Customer.objects.all()
    return render(request, 'reports/customer_statement_select.html', {
        'customers': customers
    })


# =========================
# CUSTOMER STATEMENT - FINAL
# =========================
def customer_statement(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    invoices = Invoice.objects.filter(customer=customer)
    payments = Payment.objects.filter(invoice__customer=customer)

    entries = []

    # INVOICES → Debit
    for inv in invoices:
        entries.append({
            'date': inv.date,                  # date
            'desc': f'Invoice #{inv.id}',
            'debit': inv.total,
            'credit': None
        })

    # PAYMENTS → Credit
    for pay in payments:
        entries.append({
            'date': pay.date.date(),           # 🔥 FIX: datetime → date
            'desc': 'Payment',
            'debit': None,
            'credit': pay.amount
        })

    # sort by date
    entries.sort(key=lambda x: x['date'])

    # running balance
    balance = 0
    for e in entries:
        if e['debit']:
            balance += e['debit']
        if e['credit']:
            balance -= e['credit']
        e['balance'] = balance

    return render(request, 'reports/customer_statement.html', {
        'customer': customer,
        'entries': entries
    })
from django.db.models import Sum, F
from invoices.models import InvoiceItem
from django.shortcuts import render

def top_products(request):
    items = (
        InvoiceItem.objects
        .values('product__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        )
        .order_by('-total_qty')
    )

    return render(request, 'reports/top_products.html', {
        'items': items
    })
