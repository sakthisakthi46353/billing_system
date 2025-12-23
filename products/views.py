from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {
        "products": products
    })


# ======================
# ADD PRODUCT
# ======================
from django.shortcuts import render, redirect
from .models import Product

def product_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        Product.objects.create(
            name=name,
            price=price,
            stock=stock
        )

        return redirect("products:product_list")  # 👈 redirect works now

    return render(request, "products/product_add.html")


# ======================
# VIEW PRODUCT
# ======================
def product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_view.html", {
        "product": product
    })


# ======================
# EDIT PRODUCT
# ======================
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.save()

        return redirect("products:product_list")

    return render(request, "products/product_edit.html", {
        "product": product
    })

# ======================
# DELETE PRODUCT
# ======================
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("products:product_list")
