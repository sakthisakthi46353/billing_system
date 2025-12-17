from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # DASHBOARD / HOME (core)
    path('', include('core.urls')),

    # APP MODULES
    path('customers/', include('customers.urls')),
    path('products/', include('products.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),

    # REPORTS MODULE
    path('reports/', include('reports.urls')),
]
