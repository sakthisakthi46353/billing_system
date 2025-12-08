from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('products/', include('products.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),
]
