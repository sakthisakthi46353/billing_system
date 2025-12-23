from django.shortcuts import render, redirect, get_object_or_404
from .models import Purchase, PurchaseItem
from suppliers.models import Supplier
from products.models import Product

def purchase_list(request):
    purchases = Purchase.objects.all().order_by("-id")
    return render(request, "purchases/purchase_list.html", {
        "purchases": purchases
    })


def purchase_add(request):
    suppliers = Supplier.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        product_id = request.POST.get("product")
        qty = int(request.POST.get("quantity"))
        price = request.POST.get("unit_price")

        supplier = Supplier.objects.get(id=supplier_id)
        product = Product.objects.get(id=product_id)

        purchase = Purchase.objects.create(supplier=supplier)

        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            quantity=qty,
            unit_price=price
        )

        # ✅ STOCK INCREASE
        product.stock += qty
        product.save()

        return redirect("purchases:purchase_list")

    return render(request, "purchases/purchase_add.html", {
        "suppliers": suppliers,
        "products": products
    })


def purchase_view(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, "purchases/purchase_view.html", {
        "purchase": purchase
    })


def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase.delete()
    return redirect("purchases:purchase_list")
