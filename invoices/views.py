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
    invoices = Invoice.objects.select_related('customer').all()
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
        customer_id = request.POST.get("customer")

        if not customer_id:
            messages.error(request, "Please select customer")
            return redirect("invoice_add")

        customer = get_object_or_404(Customer, id=customer_id)

        invoice = Invoice.objects.create(
            customer=customer,
            total=Decimal("0.00"),
            status="UNPAID"
        )

        grand_total = Decimal("0.00")

        for i in range(1, 4):
            product_id = request.POST.get(f"product_{i}")
            qty = request.POST.get(f"qty_{i}")

            if not product_id or not qty:
                continue

            qty = int(qty)
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=product_id)

            if product.stock < qty:
                messages.error(
                    request,
                    f"Not enough stock for {product.name}"
                )
                raise transaction.TransactionManagementError("Stock error")

            line_total = product.price * qty
            grand_total += line_total

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=product.price
            )

            product.stock -= qty
            product.save()

        if grand_total == 0:
            messages.error(request, "Please add at least one product")
            invoice.delete()
            return redirect("invoice_add")

        invoice.total = grand_total
        invoice.save()

        messages.success(request, "Invoice saved successfully")
        return redirect("invoice_list")

    return render(request, "invoices/invoice_add.html", {
        "customers": customers,
        "products": products
    })


# ================================
# VIEW INVOICE
# ================================
def invoice_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    items = invoice.items.all()
    total_paid = invoice.payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal("0.00")

    balance = invoice.total - total_paid

    return render(request, 'invoices/invoice_view.html', {
        'invoice': invoice,
        'items': items,
        'total_paid': total_paid,
        'balance': balance
    })


# ================================
# EDIT INVOICE
# ================================
@transaction.atomic
@transaction.atomic
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        # update customer
        invoice.customer_id = request.POST.get("customer")

        # restore stock
        for item in invoice.items.all():
            item.product.stock += item.quantity
            item.product.save()

        invoice.items.all().delete()

        grand_total = Decimal("0.00")

        product_ids = request.POST.getlist("product")
        quantities = request.POST.getlist("quantity")

        for prod_id, qty_str in zip(product_ids, quantities):
            if not prod_id or not qty_str:
                continue

            qty = int(qty_str)
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=prod_id)

            if product.stock < qty:
                messages.error(request, f"Not enough stock for {product.name}")
                raise transaction.TransactionManagementError("Stock error")

            line_total = product.price * qty
            grand_total += line_total

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=product.price
            )

            product.stock -= qty
            product.save()

        invoice.total = grand_total
        invoice.save()

        messages.success(request, "Invoice updated successfully")
        return redirect('invoice_view', pk=invoice.id)

    return render(request, 'invoices/invoice_edit.html', {
        'invoice': invoice,
        'items': invoice.items.all(),
        'products': products,
        'customers': customers
    })


# ================================
# DELETE INVOICE
# ================================
@transaction.atomic
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    Payment.objects.filter(invoice=invoice).delete()

    for item in invoice.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()

    invoice.delete()
    messages.error(request, "Invoice deleted")
    return redirect('invoice_list')
