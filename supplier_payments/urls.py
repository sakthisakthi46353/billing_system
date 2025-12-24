from django.urls import path
from . import views

app_name = "supplier_payments"

urlpatterns = [
    path('', views.supplier_payment_list, name='payment_list'),
    path('add/', views.supplier_payment_add, name='payment_add'),
]
