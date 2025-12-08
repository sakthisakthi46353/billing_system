from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from .models import Payment
from invoices.models import Invoice


# ================================
# PAYMENT LIST ( /payments/ )
# ================================
def payment_list(request):
    payments = Payment.objects.all().order_by('-date')
    return render(request, 'payments/payment_list.html', {
        'payments': payments
    })


# ================================
# ADD PAYMENT
# ================================
@transaction.atomic
def payment_add(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        amount = request.POST.get('amount')

        if not amount:
            messages.error(request, "Please enter an amount")
            return redirect('payment_add', invoice_id=invoice_id)

        # Save payment
        payment = Payment.objects.create(
            invoice=invoice,
            amount=amount
        )

        # Update invoice status after payment
        invoice.update_status()

        messages.success(request, "Payment added successfully")
        return redirect('payment_list')

    return render(request, 'payments/payment_add.html', {
        'invoice': invoice,
        'balance': invoice.balance,
        'paid': invoice.paid_amount,
    })


# ================================
# PAYMENT HISTORY PAGE
# ================================
def payment_history(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payments = Payment.objects.filter(invoice=invoice).order_by('date')

    total = invoice.total
    history = []

    balance = total

    for p in payments:
        balance -= p.amount
        history.append({
            'date': p.date,
            'amount': p.amount,
            'balance': balance
        })

    return render(request, 'payments/history.html', {
        'invoice': invoice,
        'history': history,
    })
def payment_choose_invoice(request):
    invoices = Invoice.objects.all()
    return render(request, 'payments/payment_choose_invoice.html', {
        'invoices': invoices
    })

