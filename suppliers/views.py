from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier

from django.shortcuts import render
from django.shortcuts import render
from .models import Supplier

from django.shortcuts import render
from .models import Supplier
from django.shortcuts import render

def supplier_list(request):
    return render(request, "suppliers/supplier_list.html")


# ADD
def supplier_add(request):
    if request.method == "POST":
        Supplier.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
        )
        return redirect("suppliers:supplier_list")

    return render(request, "suppliers/supplier_add.html")

# EDIT
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier.name = request.POST.get("name")
        supplier.phone = request.POST.get("phone")
        supplier.email = request.POST.get("email")
        supplier.address = request.POST.get("address")
        supplier.save()
        return redirect("suppliers:supplier_list")

    return render(request, "suppliers/supplier_edit.html", {
        "supplier": supplier
    })

# DELETE
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect("suppliers:supplier_list")
from django.db.models import Sum
from invoices.models import InvoiceItem
from decimal import Decimal

def dashboard(request):
    total_revenue = InvoiceItem.objects.aggregate(
        total=Sum("unit_price")
    )["total"] or Decimal("0.00")

    return render(request, "dashboard/dashboard.html", {
        "total_revenue": total_revenue,
    })
from django.shortcuts import render
