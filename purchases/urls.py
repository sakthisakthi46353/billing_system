from django.urls import path
from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.purchase_list, name="purchase_list"),
    path("add/", views.purchase_add, name="purchase_add"),
    path("<int:pk>/", views.purchase_view, name="purchase_view"),
    path("<int:pk>/delete/", views.purchase_delete, name="purchase_delete"),
]
