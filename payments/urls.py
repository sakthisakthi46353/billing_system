from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('add/', views.payment_add, name='payment_add'),
    path('add/', views.payment_add, name='payment_add'),
    path('<int:invoice_id>/history/', views.payment_history, name='payment_history'),
    path('add/<int:invoice_id>/', views.payment_add, name='payment_add')

]
