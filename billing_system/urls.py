from django.contrib import admin
from django.urls import path, include
from dashboard.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),

    path("customers/", include("customers.urls")),
    path("products/", include("products.urls")),
    path("invoices/", include("invoices.urls")),  # ✅ MUST
    path("payments/", include("payments.urls")),
    path("reports/", include("reports.urls")),
    path("suppliers/", include("suppliers.urls")),

]
