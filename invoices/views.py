from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from .models import Invoice, InvoiceItem
from customers.models import Customer
from products.models import Product
from payments.models import Payment


# ================================
# LIST INVOICES
# ================================
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


# ================================
# ADD NEW INVOICE
# ================================
@transaction.atomic
def invoice_add(request):
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get('customer')
        if not customer_id:
            messages.error(request, "Please select a customer")
            return redirect('invoice_add')

        customer = get_object_or_404(Customer, id=customer_id)

        # create invoice
        invoice = Invoice.objects.create(customer=customer)

        subtotal = Decimal('0')

        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        for prod_id, qty_str in zip(product_ids, quantities):

            if not prod_id or not qty_str:
                continue

            qty = int(qty_str)
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=prod_id)

            # check stock
            if product.stock < qty:
                messages.error(request, f"Not enough stock for {product.name}")
                raise transaction.TransactionManagementError("Stock error")

            # create invoice item
            item = InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=product.price
            )

            subtotal += item.price * item.quantity

            # reduce stock
            product.stock -= qty
            product.save()

        # calculate tax & total
        tax = subtotal * Decimal('0.10')  # 10%
        total = subtotal + tax

        invoice.subtotal = subtotal
        invoice.tax = tax
        invoice.total = total
        invoice.save()

        messages.success(request, f"Invoice #{invoice.id} created successfully")
        return redirect('/')

    return render(request, 'invoices/invoice_add.html', {
        'customers': customers,
        'products': products,
    })


# ================================
# INVOICE DETAIL PAGE
# ================================
def invoice_detail(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    items = invoice.items.all()
    payments = invoice.payments.all()

    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    })


# ================================
# EDIT INVOICE
# ================================
def invoice_edit(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    customers = Customer.objects.all()

    if request.method == "POST":
        invoice.customer = Customer.objects.get(id=request.POST['customer'])
        invoice.save()
        messages.success(request, "Invoice updated")
        return redirect('/')

    return render(request, 'invoices/invoice_edit.html', {
        'invoice': invoice,
        'customers': customers,
    })


# ================================
# DELETE INVOICE
# ================================
def invoice_delete(request, id):
    invoice = get_object_or_404(Invoice, id=id)

    # delete all payments before deleting invoice
    Payment.objects.filter(invoice=invoice).delete()

    invoice.delete()
    messages.error(request, "Invoice deleted")
    return redirect('/')

def invoice_view(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    return render(request, 'invoices/invoice_view.html', {
        'invoice': invoice,
        'items': invoice.items.all(),
        'payments': invoice.payments.all(),
    })

def invoice_view(request, pk):
    invoice = Invoice.objects.get(id=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)
    payments = Payment.objects.filter(invoice=invoice)

    paid_amount = sum(p.amount for p in payments)
    balance = invoice.total - paid_amount

    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'paid_amount': paid_amount,
        'balance': balance,
    }
    return render(request, "invoices/invoice_view.html", context)
