from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [

    # 🔹 Payment list
    path(
        "",
        views.payment_list,
        name="payment_list"
    ),

    # 🔹 Add payment (normal)
    path(
        "add/",
        views.payment_add,
        name="payment_add"
    ),

    # 🔹 Add payment from invoice
    path(
        "add/<int:invoice_id>/",
        views.payment_add,
        name="payment_add_invoice"
    ),

    # 🔹 Edit payment  ✅ (IMPORTANT ORDER)
    path(
        "<int:pk>/edit/",
        views.payment_edit,
        name="payment_edit"
    ),

    # 🔹 Delete payment
    path(
        "<int:pk>/delete/",
        views.payment_delete,
        name="payment_delete"
    ),

    # 🔹 Payment history by invoice
    path(
        "invoice/<int:invoice_id>/history/",
        views.payment_history,
        name="payment_history"
    ),
]
