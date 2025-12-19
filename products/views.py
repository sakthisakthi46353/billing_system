from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

# ======================
# PRODUCT LIST
# ======================
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products
    })


# ======================
# ADD PRODUCT
# ======================
def product_add(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            stock=request.POST.get('stock')
        )
        return redirect('product_list')

    return render(request, 'products/product_add.html')


# ======================
# EDIT PRODUCT
# ======================
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.save()
        return redirect('product_list')

    return render(request, 'products/product_edit.html', {
        'product': product
    })


# ======================
# DELETE PRODUCT
# ======================
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')
    
def product_view(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, "products/product_view.html", {
        "product": product
    })
