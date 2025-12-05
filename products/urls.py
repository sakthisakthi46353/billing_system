from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("add/", views.product_add, name="product_add"),
    path("<int:id>/", views.product_view, name="product_view"),
    path("<int:id>/edit/", views.product_edit, name="product_edit"),
    path("<int:id>/delete/", views.product_delete, name="product_delete"),
]
