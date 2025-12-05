from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer

# List Customers
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customers/list.html", {"customers": customers})


# Add Customer
def customer_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        Customer.objects.create(name=name, email=email)
        return redirect("/customers/")
    return render(request, "customers/add.html")


# View Customer
def customer_view(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, "customers/view.html", {"customer": customer})


# Edit Customer
def customer_edit(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.email = request.POST.get("email")
        customer.save()
        return redirect("/customers/")

    return render(request, "customers/edit.html", {"customer": customer})


# Delete Customer
def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.delete()
        return redirect("/customers/")

    return render(request, "customers/delete.html", {"customer": customer})
