from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('customer-balance/', views.customer_balance, name='customer_balance'),
]
app_name = "reports"

path(
    "customer-statement/<int:customer_id>/",
    views.customer_statement,
    name="customer_statement"
)

urlpatterns = [
    # =========================
    # REPORTS HOME
    # =========================
    path(
        "",
        views.reports_home,
        name="reports_home"
    ),

    # =========================
    # CUSTOMER BALANCE REPORT
    # =========================
    path(
        "customer-balance/",
        views.customer_balance,
        name="customer_balance"
    ),

    # =========================
    # SALES SUMMARY REPORT
    # =========================
    path(
        "sales-summary/",
        views.sales_summary,
        name="sales_summary"
    ),

    # =========================
    # TOP PRODUCTS REPORT
    # =========================
    path(
        "top-products/",
        views.top_products,
        name="top_products"
    ),

    # =========================
    # CUSTOMER STATEMENT
    # =========================
    path(
        "customer-statement/",
        views.customer_statement_select,
        name="customer_statement_select"
    ),

    path(
        "customer-statement/<int:customer_id>/",
        views.customer_statement,
        name="customer_statement"
    ),


    
]

app_name = "reports"


lpatterns = [
    path("customer-balance/", views.customer_balance, name="customer_balance"),
]
