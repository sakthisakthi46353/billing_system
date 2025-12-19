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
def payment_add(request):
    invoices = Invoice.objects.all()

    if request.method == "POST":
        invoice_id = request.POST.get('invoice')
        amount = request.POST.get('amount')

        if not invoice_id or not amount:
            return render(request, 'payments/payment_add.html', {
                'invoices': invoices,
                'error': 'Invoice and Amount are required'
            })

        invoice = get_object_or_404(Invoice, id=invoice_id)

        # Create payment
        Payment.objects.create(
            invoice=invoice,
            amount=amount
        )

        # Calculate total paid
        total_paid = invoice.payments.aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        # Update invoice status
        if total_paid == 0:
            invoice.status = "UNPAID"
        elif total_paid < invoice.total:
            invoice.status = "PARTIALLY_PAID"
        else:
            invoice.status = "PAID"

        invoice.save()

        return redirect('payment_list')

    return render(request, 'payments/payment_add.html', {
        'invoices': invoices
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
