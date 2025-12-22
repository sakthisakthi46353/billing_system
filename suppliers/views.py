from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "suppliers/supplier_list.html", {
        "suppliers": suppliers
    })


def supplier_create(request):
    if request.method == "POST":
        Supplier.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
        )
        return redirect("supplier_list")

    return render(request, "suppliers/supplier_form.html")


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier.name = request.POST.get("name")
        supplier.phone = request.POST.get("phone")
        supplier.email = request.POST.get("email")
        supplier.address = request.POST.get("address")
        supplier.save()
        return redirect("supplier_list")

    return render(request, "suppliers/supplier_form.html", {
        "supplier": supplier
    })


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier.delete()
        return redirect("supplier_list")

    return render(request, "suppliers/supplier_confirm_delete.html", {
        "supplier": supplier
    })

from django.shortcuts import render, get_object_or_404
from .models import Supplier
from purchases.models import Purchase
from supplier_payments.models import SupplierPayment


def supplier_ledger(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    purchases = Purchase.objects.filter(supplier=supplier)
    payments = SupplierPayment.objects.filter(supplier=supplier)

    ledger = []

    # Purchases = DEBIT
    for p in purchases:
        ledger.append({
            "date": p.date,
            "type": "Purchase",
            "description": f"Purchase #{p.id}",
            "debit": p.total_amount,
            "credit": 0
        })

    # Payments = CREDIT
    for pay in payments:
        ledger.append({
            "date": pay.date,
            "type": "Payment",
            "description": pay.method.upper(),
            "debit": 0,
            "credit": pay.amount
        })

    # sort by date
    ledger.sort(key=lambda x: x["date"])

    # running balance
    balance = 0
    for row in ledger:
        balance += row["debit"] - row["credit"]
        row["balance"] = balance

    return render(request, "suppliers/supplier_ledger.html", {
        "supplier": supplier,
        "ledger": ledger
    })
