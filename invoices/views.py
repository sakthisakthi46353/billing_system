from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum

from .models import Invoice, InvoiceItem
from customers.models import Customer
from products.models import Product
from payments.models import Payment


# ================================
# LIST INVOICES
# ================================
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-id')
    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices
    })


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

            if product.stock < qty:
                messages.error(
                    request,
                    f"Not enough stock for {product.name}"
                )
                raise transaction.TransactionManagementError("Stock error")

            item = InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=product.price
            )

            subtotal += item.price * item.quantity
            product.stock -= qty
            product.save()

        tax = subtotal * Decimal('0.10')
        total = subtotal + tax

        invoice.subtotal = subtotal
        invoice.tax = tax
        invoice.total = total
        invoice.save()

        messages.success(
            request,
            f"Invoice #{invoice.id} created successfully"
        )
        return redirect('invoice_view', pk=invoice.id)

    return render(request, 'invoices/invoice_add.html', {
        'customers': customers,
        'products': products,
    })


# ================================
# VIEW INVOICE
# ================================
def invoice_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    items = invoice.items.all()

    total_paid = invoice.payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    balance = invoice.total - total_paid

    return render(request, 'invoices/invoice_view.html', {
        'invoice': invoice,
        'items': items,
        'total_paid': total_paid,
        'balance': balance
    })


# ================================
# EDIT INVOICE (ADVANCED – STOCK REVERSE)
# ================================
@transaction.atomic
def invoice_edit(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    products = Product.objects.all()

    if request.method == "POST":

        # 1️⃣ OLD ITEMS → STOCK BACK
        old_items = InvoiceItem.objects.filter(invoice=invoice)
        for item in old_items:
            product = item.product
            product.stock += item.quantity
            product.save()

        # 2️⃣ DELETE OLD ITEMS
        old_items.delete()

        subtotal = Decimal('0')

        # 3️⃣ ADD NEW ITEMS → STOCK REDUCE
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        for prod_id, qty_str in zip(product_ids, quantities):
            if not prod_id or not qty_str:
                continue

            qty = int(qty_str)
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=prod_id)

            if product.stock < qty:
                messages.error(
                    request,
                    f"Not enough stock for {product.name}"
                )
                raise transaction.TransactionManagementError("Stock error")

            item = InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=product.price
            )

            subtotal += item.price * item.quantity
            product.stock -= qty
            product.save()

        # 4️⃣ RECALCULATE TOTAL
        tax = subtotal * Decimal('0.10')
        total = subtotal + tax

        invoice.subtotal = subtotal
        invoice.tax = tax
        invoice.total = total
        invoice.save()

        messages.success(
            request,
            f"Invoice #{invoice.id} updated successfully"
        )
        return redirect('invoice_view', pk=invoice.id)

    items = invoice.items.all()

    return render(request, 'invoices/invoice_edit.html', {
        'invoice': invoice,
        'items': items,
        'products': products
    })


# ================================
# DELETE INVOICE
# ================================
@transaction.atomic
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    # delete payments
    Payment.objects.filter(invoice=invoice).delete()

    # restore stock
    for item in invoice.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()

    invoice.delete()
    messages.error(request, "Invoice deleted")
    return redirect('invoice_list')
