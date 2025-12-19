from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer


# =========================
# CUSTOMER LIST
# =========================
def customer_list(request):
    customers = Customer.objects.all().order_by('id')
    return render(request, 'customers/customer_list.html', {
        'customers': customers
    })


# =========================
# ADD CUSTOMER
# =========================
def customer_add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        Customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        return redirect('customer_list')

    return render(request, 'customers/customer_add.html')


# =========================
# EDIT CUSTOMER
# =========================
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.save()

        return redirect('customer_list')

    return render(request, 'customers/customer_edit.html', {
        'customer': customer
    })


# =========================
# DELETE CUSTOMER
# =========================
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')
