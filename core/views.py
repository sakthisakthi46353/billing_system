from django.shortcuts import render
from django.db.models import Sum, F

from customers.models import Customer
from products.models import Product
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


# ============================
# DASHBOARD
# ============================
def home(request):
    customers = Customer.objects.all()
    products = Product.objects.all()
    invoices = Invoice.objects.all()
    payments = Payment.objects.all()

    return render(request, 'core/home.html', {
        'customers': customers,
        'products': products,
        'invoices': invoices,
        'payments': payments,
    })


# ============================
# REPORTS MENU
# ============================
def reports_home(request):
    return render(request, 'core/reports_home.html')


# ============================
# CUSTOMER BALANCE SUMMARY
# ============================
def customer_balance(request):
    customers = Customer.objects.all()
    report = []

    for c in customers:
        invoiced = Invoice.objects.filter(customer=c).aggregate(Sum('total'))['total__sum'] or 0
        paid = Payment.objects.filter(invoice__customer=c).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = invoiced - paid

        report.append({
            'customer': c,
            'invoiced': invoiced,
            'paid': paid,
            'balance': balance,
        })

    return render(request, 'core/customer_balance.html', {
        'report': report
    })


# ============================
# SALES SUMMARY
# ============================
def sales_summary(request):
    total_invoices = Invoice.objects.count()
    total_sales = Invoice.objects.aggregate(sum=Sum('total'))['sum'] or 0
    total_payments = Payment.objects.aggregate(sum=Sum('amount'))['sum'] or 0

    avg_invoice = total_sales / total_invoices if total_invoices > 0 else 0

    return render(request, 'core/sales_summary.html', {
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
        qty=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-qty')

    return render(request, 'core/top_products.html', {
        'items': items
    })


# ============================
# CUSTOMER STATEMENT
# ============================
def customer_statement(request):
    return render(request, 'core/customer_statement.html')
def customer_statement(request, customer_id):
    customer = Customer.objects.get(id=customer_id)

    # Get invoices and payments sorted by date
    events = []

    for inv in Invoice.objects.filter(customer=customer):
        events.append({
            'date': inv.date,
            'type': 'invoice',
            'description': f'Invoice #{inv.id}',
            'amount': inv.total,
        })

    for pay in Payment.objects.filter(invoice__customer=customer):
        events.append({
            'date': pay.date,
            'type': 'payment',
            'description': 'Payment',
            'amount': -pay.amount,
        })

    # Sort by date
    events = sorted(events, key=lambda x: x['date'])

    # Running balance
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

    return render(request, 'core/customer_statement.html', {
        'customer': customer,
        'history': history
    })
def customer_statement(request, customer_id=None):
    if customer_id is None:
        customers = Customer.objects.all()
        return render(request, 'core/customer_statement_select.html', {
            'customers': customers
        })

    customer = Customer.objects.get(id=customer_id)
    invoices = Invoice.objects.filter(customer=customer)
    payments = Payment.objects.filter(invoice__customer=customer)

    return render(request, 'core/customer_statement.html', {
        'customer': customer,
        'invoices': invoices,
        'payments': payments,
    })
