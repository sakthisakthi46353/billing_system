from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("", views.payment_list, name="payment_list"),

    # add payment (normal)
    path("add/", views.payment_add, name="payment_add"),

    # add payment for specific invoice
    path("add/<int:invoice_id>/", views.payment_add, name="payment_add_invoice"),

    path("<int:pk>/edit/", views.payment_edit, name="payment_edit"),
    path("<int:pk>/delete/", views.payment_delete, name="payment_delete"),

    path("invoice/<int:invoice_id>/history/",
         views.payment_history,
         name="payment_history"),
]
