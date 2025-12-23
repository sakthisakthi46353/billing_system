from django.shortcuts import render, redirect
from .models import Purchase, PurchaseItem
from suppliers.models import Supplier
from products.models import Product


def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-id')
    return render(request, 'purchases/purchase_list.html', {
        'purchases': purchases
    })


def purchase_add(request):
    suppliers = Supplier.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        product_id = request.POST.get("product")
        qty = int(request.POST.get("quantity"))
        price = request.POST.get("price")

        purchase = Purchase.objects.create(
            supplier_id=supplier_id
        )

        item = PurchaseItem.objects.create(
            purchase=purchase,
            product_id=product_id,
            quantity=qty,
            price=price
        )

        # 🔥 IMPORTANT: increase stock
        product = item.product
        product.stock += qty
        product.save()

        return redirect('purchases:purchase_list')

    return render(request, 'purchases/purchase_add.html', {
        'suppliers': suppliers,
        'products': products
    })
