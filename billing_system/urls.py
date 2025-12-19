from django.contrib import admin
from django.urls import path, include
from core.views import dashboard   # 👈 IMPORTANT

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ ROOT DASHBOARD (ONLY THIS)
    path('', dashboard, name='dashboard'),

    path('customers/', include('customers.urls')),
    path('products/', include('products.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
]
