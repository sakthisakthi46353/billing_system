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
    invoices = Invoice.objects.all()
    return render(request, "invoices/invoice_list.html", {
        "invoices": invoices
    })

# ================================
# ADD NEW INVOICE (DYNAMIC ROWS)
# ================================
@transaction.atomic
def invoice_add(request):
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")

        if not customer_id:
            messages.error(request, "Please select a customer")
            return redirect("invoices:invoice_add")

        customer = get_object_or_404(Customer, id=customer_id)

        # ✅ create invoice (totals calculated dynamically in view)
        invoice = Invoice.objects.create(
            customer=customer,
            status="UNPAID"
        )

        has_item = False

        product_ids = request.POST.getlist("product")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("unit_price")
        tax_percents = request.POST.getlist("tax_percent")
        discount_types = request.POST.getlist("discount_type")
        discount_values = request.POST.getlist("discount_value")

        for i in range(len(product_ids)):
            if not product_ids[i]:
                continue

            qty = int(quantities[i])
            if qty <= 0:
                continue

            product = get_object_or_404(Product, id=product_ids[i])

            if product.stock < qty:
                messages.error(
                    request,
                    f"Not enough stock for {product.name}"
                )
                raise transaction.TransactionManagementError("Stock error")

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                unit_price=Decimal(prices[i]),
                tax_percent=Decimal(tax_percents[i]),
                discount_type=discount_types[i],
                discount_value=Decimal(discount_values[i]),
            )

            product.stock -= qty
            product.save()

            has_item = True

        if not has_item:
            invoice.delete()
            messages.error(request, "Please add at least one item")
            return redirect("invoices:invoice_add")

        messages.success(request, "Invoice created successfully")
        return redirect("invoices:invoice_list")

    return render(request, "invoices/invoice_add.html", {
        "customers": customers,
        "products": products
    })


# ================================
# VIEW INVOICE
# ================================
from django.shortcuts import render, get_object_or_404
from decimal import Decimal

from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


def invoice_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)

    # ✅ Calculate subtotal MANUALLY (NOT ORM)
    subtotal = Decimal("0.00")
    for item in items:
        subtotal += item.line_total   # ✅ property OK

    total_discount = Decimal("0.00")
    total_tax = Decimal("0.00")

    grand_total = subtotal + total_tax - total_discount

    paid = Payment.objects.filter(
        customer=invoice.customer
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    balance = grand_total - paid

    return render(request, "invoices/invoice_view.html", {
        "invoice": invoice,
        "items": items,
        "subtotal": subtotal,
        "total_discount": total_discount,
        "total_tax": total_tax,
        "grand_total": grand_total,
        "paid": paid,
        "balance": balance,
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
    return redirect("invoices:invoice_list")

from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Sum

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os

from .models import Invoice
from payments.models import Payment


def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    # -----------------------------
    # PDF RESPONSE
    # -----------------------------
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{invoice.id}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # -----------------------------
    # FONT (₹ SUPPORT)
    # -----------------------------
    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVu", font_path))
    c.setFont("DejaVu", 11)

    # -----------------------------
    # LOGO
    # -----------------------------
    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            40, height - 80,
            width=120,
            height=50,
            preserveAspectRatio=True,
            mask="auto"
        )

    # -----------------------------
    # HEADER
    # -----------------------------
    c.setFont("DejaVu", 18)
    c.drawRightString(width - 40, height - 50, "INVOICE")

    c.setFont("DejaVu", 11)
    c.drawRightString(width - 40, height - 80, f"Invoice No: {invoice.id}")
    c.drawRightString(width - 40, height - 100, f"Date: {invoice.date}")

    # -----------------------------
    # CUSTOMER DETAILS
    # -----------------------------
    y = height - 140
    c.drawString(40, y, "Bill To:")
    c.drawString(40, y - 20, invoice.customer.name)
    c.drawString(40, y - 40, f"Status: {invoice.status}")

    # -----------------------------
    # TABLE HEADER
    # -----------------------------
    y -= 80
    c.line(40, y, width - 40, y)
    y -= 20

    c.drawString(40, y, "Product")
    c.drawString(260, y, "Qty")
    c.drawString(320, y, "Unit Price")
    c.drawRightString(width - 40, y, "Line Total")

    y -= 10
    c.line(40, y, width - 40, y)
    y -= 25

    # -----------------------------
    # TABLE ROWS
    # -----------------------------
    subtotal = Decimal("0.00")
    total_discount = Decimal("0.00")
    total_tax = Decimal("0.00")

    for item in items:
        base = item.unit_price * item.quantity

        if item.discount_type == "percent":
            discount = base * (item.discount_value / Decimal("100"))
        else:
            discount = item.discount_value

        taxable = base - discount
        tax = taxable * (item.tax_percent / Decimal("100"))
        line_total = taxable + tax

        subtotal += base
        total_discount += discount
        total_tax += tax

        c.drawString(40, y, item.product.name)
        c.drawString(260, y, str(item.quantity))
        c.drawString(320, y, f"₹ {item.unit_price:.2f}")
        c.drawRightString(width - 40, y, f"₹ {line_total:.2f}")

        y -= 25

    # -----------------------------
    # TOTALS
    # -----------------------------
    grand_total = subtotal - total_discount + total_tax

    paid = Payment.objects.filter(
        invoice=invoice
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    balance = grand_total - paid

    y -= 20
    c.line(300, y, width - 40, y)
    y -= 20

    c.drawRightString(420, y, "Subtotal:")
    c.drawRightString(width - 40, y, f"₹ {subtotal:.2f}")

    y -= 20
    c.drawRightString(420, y, "Discount:")
    c.drawRightString(width - 40, y, f"₹ {total_discount:.2f}")

    y -= 20
    c.drawRightString(420, y, "Tax:")
    c.drawRightString(width - 40, y, f"₹ {total_tax:.2f}")

    y -= 25
    c.setFont("DejaVu", 12)
    c.drawRightString(420, y, "Grand Total:")
    c.drawRightString(width - 40, y, f"₹ {grand_total:.2f}")

    y -= 25
    c.setFont("DejaVu", 11)
    c.drawRightString(420, y, "Paid:")
    c.drawRightString(width - 40, y, f"₹ {paid:.2f}")

    y -= 20
    c.drawRightString(420, y, "Balance:")
    c.drawRightString(width - 40, y, f"₹ {balance:.2f}")

    c.showPage()
    c.save()

    return response
from django.shortcuts import get_object_or_404, render
from decimal import Decimal
from django.db.models import Sum

from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)

    # ✅ Subtotal calculation (NO ORM Sum on line_total)
    subtotal = Decimal("0.00")
    for item in items:
        subtotal += item.line_total

    total_discount = Decimal("0.00")
    total_tax = Decimal("0.00")

    grand_total = subtotal + total_tax - total_discount

    # ✅ FIX HERE (customer based payment)
    paid = Payment.objects.filter(
        customer=invoice.customer
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    balance = grand_total - paid

    return render(request, "invoices/invoice_pdf.html", {
        "invoice": invoice,
        "items": items,
        "subtotal": subtotal,
        "total_discount": total_discount,
        "total_tax": total_tax,
        "grand_total": grand_total,
        "paid": paid,
        "balance": balance,
    })
from django.shortcuts import get_object_or_404, render
from decimal import Decimal
from django.db.models import Sum

from invoices.models import Invoice, InvoiceItem
from payments.models import Payment


