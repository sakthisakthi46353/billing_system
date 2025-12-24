from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # LOGIN as first page
    path("", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Dashboard
    path("dashboard/", include("dashboard.urls")),

    # Core apps
    path("customers/", include("customers.urls")),
    path("products/", include("products.urls")),
    path("invoices/", include("invoices.urls")),
    path("payments/", include("payments.urls")),
    path("purchases/", include("purchases.urls")),
    path("reports/", include("reports.urls")),

    # ✅ Suppliers
    path("suppliers/", include("suppliers.urls")),

    # ✅ Supplier Payments
    path("supplier-payments/", include("supplier_payments.urls")),
]
