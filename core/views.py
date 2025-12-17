from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


# ============================
# DASHBOARD / HOME
# ============================
def home(request):
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


# ============================
# REPORTS HOME
# ============================
def reports_home(request):
    return render(request, 'reports/home.html')


# ============================
# CUSTOMER BALANCE SUMMARY
# ============================
def customer_balance(request):
    report = []

    for c in Customer.objects.all():
        total_invoiced = Invoice.objects.filter(
            customer=c
        ).aggregate(total=Sum('total'))['total'] or 0

        total_paid = Payment.objects.filter(
            invoice__customer=c
        ).aggregate(total=Sum('amount'))['total'] or 0

        report.append({
            'customer': c,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance': total_invoiced - total_paid,
        })

    return render(request, 'reports/customer_balance.html', {
        'report': report
    })


# ============================
# SALES SUMMARY
# ============================
def sales_summary(request):
    total_invoices = Invoice.objects.count()
    total_sales = Invoice.objects.aggregate(
        total=Sum('total')
    )['total'] or 0

    total_payments = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    avg_invoice = total_sales / total_invoices if total_invoices else 0

    return render(request, 'reports/sales_summary.html', {
        'total_invoices': total_invoices,
        'total_sales': total_sales,
        'total_payments': total_payments,
        'avg_invoice': avg_invoice,
    })


# ============================
# TOP SELLING PRODUCTS
# ============================
def top_products(request):
    items = InvoiceItem.objects.values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_qty')

    return render(request, 'reports/top_products.html', {
        'items': items
    })


# ============================
# CUSTOMER STATEMENT (SELECT)
# ============================
def customer_statement_select(request):
    customers = Customer.objects.all()
    return render(request, 'reports/customer_statement_select.html', {
        'customers': customers
    })


# ============================
# CUSTOMER STATEMENT (DETAIL)
# ============================
def customer_statement(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    events = []

    for inv in Invoice.objects.filter(customer=customer):
        events.append({
            'date': inv.date,
            'description': f'Invoice #{inv.id}',
            'amount': inv.total,
        })

    for pay in Payment.objects.filter(invoice__customer=customer):
        events.append({
            'date': pay.date,
            'description': 'Payment',
            'amount': -pay.amount,
        })

    events = sorted(events, key=lambda x: x['date'])

    balance = 0
    history = []
    for e in events:
        balance += e['amount']
        history.append({
            'date': e['date'],
            'description': e['description'],
            'amount': e['amount'],
            'balance': balance
        })

    return render(request, 'reports/customer_statement.html', {
        'customer': customer,
        'history': history
    })
from customers.models import Customer

def customer_statement_select(request):
    customers = Customer.objects.all()
    return render(request, 'reports/customer_statement_select.html', {
        'customers': customers
    })
def dashboard(request):
    return render(request, 'core/dashboard.html')
from django.shortcuts import render

def dashboard(request):
    return render(request, 'core/dashboard.html')


def core_home(request):
    return render(request, 'core/core_home.html')
from django.shortcuts import render

def core_home(request):
    return render(request, 'core/core_home.html')
from django.shortcuts import render, get_object_or_404
from customers.models import Customer
from invoices.models import Invoice
from payments.models import Payment

def customer_statement(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = []

    # -------------------------
    # INVOICES → DEBIT
    # -------------------------
    invoices = Invoice.objects.filter(customer=customer)

    for inv in invoices:
        entries.append({
            'date': inv.date,                 # Invoice date (date)
            'desc': f'Invoice #{inv.id}',
            'debit': inv.total,
            'credit': None,
        })

    # -------------------------
    # PAYMENTS → CREDIT
    # -------------------------
    payments = Payment.objects.filter(invoice__customer=customer)

    for pay in payments:
        entries.append({
            'date': pay.date.date(),          # ✅ FIX: datetime → date
            'desc': 'Payment',
            'debit': None,
            'credit': pay.amount,
        })

    # -------------------------
    # SORT BY DATE
    # -------------------------
    entries.sort(key=lambda x: x['date'])

    # -------------------------
    # RUNNING BALANCE
    # -------------------------
    balance = 0
    for e in entries:
        if e['debit']:
            balance += e['debit']
        if e['credit']:
            balance -= e['credit']
        e['balance'] = balance

    # -------------------------
    # RENDER
    # -------------------------
    return render(request, 'reports/customer_statement.html', {
        'customer': customer,
        'entries': entries
    })
