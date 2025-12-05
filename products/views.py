from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

# List Products
def product_list(request):
    products = Product.objects.all()
    return render(request, "products/list.html", {"products": products})


# Add Product
def product_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        Product.objects.create(name=name, price=price)
        return redirect("/products/")
    return render(request, "products/add.html")


# View Product
def product_view(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "products/view.html", {"product": product})


# Edit Product
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.save()
        return redirect("/products/")

    return render(request, "products/edit.html", {"product": product})


# Delete Product
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect("/products/")

    return render(request, "products/delete.html", {"product": product})
