from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})

def product_add(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST['name'],
            price=request.POST['price'],
            stock=request.POST['stock']
        )
        return redirect('product_list')
    return render(request, 'products/add.html')

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.save()
        return redirect('product_list')
    return render(request, 'products/edit.html', {'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')
