from django.urls import path
from . import views

app_name = "invoices"

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("add/", views.invoice_add, name="invoice_add"),
    path("<int:pk>/", views.invoice_view, name="invoice_view"),
    path("<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),
    path("<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
]
