from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Payment
from invoices.models import Invoice


# =========================
# PAYMENT LIST
# =========================
def payment_list(request):
    payments = Payment.objects.select_related(
        'invoice', 'invoice__customer'
    ).all()

    return render(request, 'payments/payment_list.html', {
        'payments': payments
    })


# =========================
# ADD PAYMENT  (like products/add/)
# =========================
def payment_add(request, invoice_id=None):
    invoices = Invoice.objects.all()
    invoice = None

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        invoice_id = request.POST.get("invoice")
        amount = request.POST.get("amount")

        invoice = get_object_or_404(Invoice, id=invoice_id)

        Payment.objects.create(
            invoice=invoice,
            amount=amount
        )

        total_paid = invoice.payments.aggregate(
            Sum("amount")
        )["amount__sum"] or 0

        if total_paid == 0:
            invoice.status = "UNPAID"
        elif total_paid < invoice.total:
            invoice.status = "PARTIALLY_PAID"
        else:
            invoice.status = "PAID"

        invoice.save()
        return redirect("payments:payment_list")

    return render(request, "payments/payment_add.html", {
        "invoices": invoices,
        "invoice": invoice
    })

# =========================
# PAYMENT HISTORY (per invoice)
# =========================
def payment_history(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payments = Payment.objects.filter(invoice=invoice)

    return render(request, 'payments/history.html', {
        'invoice': invoice,
        'payments': payments
    })
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum

from .models import Payment
from invoices.models import Invoice


# =========================
# PAYMENT LIST
# =========================
def payment_list(request):
    payments = Payment.objects.select_related(
        "invoice", "invoice__customer"
    ).order_by("-date")

    return render(request, "payments/payment_list.html", {
        "payments": payments
    })


# =========================
# ADD PAYMENT
# =========================
from customers.models import Customer
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Payment
from invoices.models import Invoice


def payment_add(request, invoice_id=None):

    customers = Customer.objects.all()   # ✅ IMPORTANT
    invoices = Invoice.objects.all()
    invoice = None

    # if coming from invoice page
    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":

        customer_id = request.POST.get("customer")
        amount = request.POST.get("amount")

        if not customer_id or not amount:
            return render(request, "payments/payment_add.html", {
                "customers": customers,
                "invoices": invoices,
                "error": "Customer and Amount required"
            })

        # 🔥 get oldest unpaid invoice for customer
        invoice = Invoice.objects.filter(
            customer_id=customer_id
        ).order_by("date").first()

        if not invoice:
            return render(request, "payments/payment_add.html", {
                "customers": customers,
                "invoices": invoices,
                "error": "No invoice found for this customer"
            })

        Payment.objects.create(
            invoice=invoice,
            amount=Decimal(amount)
        )

        # 🔄 update invoice status
        total_paid = invoice.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        if total_paid == 0:
            invoice.status = "UNPAID"
        elif total_paid < invoice.total:
            invoice.status = "PARTIALLY_PAID"
        else:
            invoice.status = "PAID"

        invoice.save()

        return redirect("payments:payment_list")

    return render(request, "payments/payment_add.html", {
        "customers": customers,   # ✅ MUST
        "invoices": invoices,
        "invoice": invoice
    })


# =========================
# VIEW PAYMENT
# =========================
def payment_view(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related(
            "invoice", "invoice__customer"
        ),
        pk=pk
    )

    return render(request, "payments/payment_view.html", {
        "payment": payment
    })


# =========================
# EDIT PAYMENT
# =========================
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    invoices = Invoice.objects.select_related("customer").all()

    if request.method == "POST":
        invoice_id = request.POST.get("invoice")
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        method = request.POST.get("method")

        if not invoice_id or not amount:
            messages.error(request, "Invoice and Amount are required")
            return redirect("payments:payment_edit", pk=pk)

        old_invoice = payment.invoice

        payment.invoice = get_object_or_404(Invoice, id=invoice_id)
        payment.amount = Decimal(amount)
        payment.date = date
        payment.method = method
        payment.save()

        # update both invoices
        _update_invoice_status(old_invoice)
        _update_invoice_status(payment.invoice)

        messages.success(request, "Payment updated successfully")
        return redirect("payments:payment_list")

    return render(request, "payments/payment_edit.html", {
        "payment": payment,
        "invoices": invoices
    })


# =========================
# DELETE PAYMENT
# =========================
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    invoice = payment.invoice

    payment.delete()
    _update_invoice_status(invoice)

    messages.error(request, "Payment deleted")
    return redirect("payments:payment_list")


def payment_history(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payments = Payment.objects.filter(invoice=invoice)

    # calculate totals
    from decimal import Decimal
    from django.db.models import Sum

    total = Decimal("0.00")
    paid = payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    # calculate invoice total dynamically
    for item in invoice.items.all():
        total += item.unit_price * item.quantity

    balance = total - paid

    return render(request, "payments/payment_history.html", {
        "invoice": invoice,
        "payments": payments,
        "total": total,
        "paid": paid,
        "balance": balance,
    })

from decimal import Decimal
from django.db.models import Sum

def _update_invoice_status(invoice):
    """
    Dynamically calculate invoice total from InvoiceItem
    """

    items = invoice.items.all()

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

        subtotal += base
        total_discount += discount
        total_tax += tax

    grand_total = subtotal - total_discount + total_tax

    total_paid = invoice.payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    if total_paid == 0:
        invoice.status = "UNPAID"
    elif total_paid < grand_total:
        invoice.status = "PARTIALLY_PAID"
    else:
        invoice.status = "PAID"

    invoice.save()
