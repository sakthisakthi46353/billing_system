from django.shortcuts import render, redirect
from suppliers.models import Supplier
from .models import SupplierPayment


def supplier_payment_list(request):
    payments = SupplierPayment.objects.select_related(
        'supplier'
    ).order_by('-id')

    return render(
        request,
        'supplier_payments/payment_list.html',
        {'payments': payments}
    )


def supplier_payment_add(request):
    suppliers = Supplier.objects.all()
    methods = SupplierPayment.PAYMENT_METHOD_CHOICES

    if request.method == "POST":
        SupplierPayment.objects.create(
            supplier_id=request.POST.get("supplier"),
            date=request.POST.get("date"),
            payment_method=request.POST.get("payment_method"),
            amount=request.POST.get("amount")
        )
        return redirect('supplier_payments:payment_list')

    return render(
        request,
        'supplier_payments/payment_add.html',
        {
            'suppliers': suppliers,
            'methods': methods
        }
    )
