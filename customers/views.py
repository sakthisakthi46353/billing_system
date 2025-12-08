from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers/list.html', {'customers': customers})

def customer_add(request):
    if request.method == "POST":
        Customer.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            address=request.POST['address'],
        )
        return redirect('customer_list')
    return render(request, 'customers/add.html')

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.name = request.POST['name']
        customer.email = request.POST['email']
        customer.phone = request.POST['phone']
        customer.address = request.POST['address']
        customer.save()
        return redirect('customer_list')
    return render(request, 'customers/edit.html', {'customer': customer})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')
