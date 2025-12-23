# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("", views.payment_list, name="payment_list"),

    # add payment for a specific invoice (invoice_id required)
    path("add/<int:invoice_id>/", views.payment_add, name="payment_add_invoice"),

    path("<int:pk>/edit/", views.payment_edit, name="payment_edit"),
    path("<int:pk>/delete/", views.payment_delete, name="payment_delete"),

    path("invoice/<int:invoice_id>/history/",
         views.payment_history,
         name="payment_history"),
]
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [

    # =========================
    # PAYMENT LIST
    # =========================
    path(
        "",
        views.payment_list,
        name="payment_list"
    ),

    # =========================
    # ADD PAYMENT (GENERAL)
    # =========================
    path(
        "add/",
        views.payment_add,
        name="payment_add"
    ),

    # =========================
    # ADD PAYMENT FOR INVOICE
    # =========================
    path(
        "add/<int:invoice_id>/",
        views.payment_add,
        name="payment_add_invoice"
    ),

    # =========================
    # EDIT / DELETE
    # =========================
    path(
        "<int:pk>/edit/",
        views.payment_edit,
        name="payment_edit"
    ),

    path(
        "<int:pk>/delete/",
        views.payment_delete,
        name="payment_delete"
    ),

    # =========================
    # PAYMENT HISTORY
    # =========================
    path(
        "invoice/<int:invoice_id>/history/",
        views.payment_history,
        name="payment_history"
    ),
]
