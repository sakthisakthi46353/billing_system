from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "suppliers/supplier_list.html", {
        "suppliers": suppliers
    })

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

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect("suppliers:supplier_list")
