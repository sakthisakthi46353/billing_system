from django.urls import path
from core import views   # IMPORTANT

urlpatterns = [
    path('', views.reports_home, name='reports_home'),

    path(
        'customer-balance/',
        views.customer_balance,
        name='customer_balance'
    ),

    path(
        'sales-summary/',
        views.sales_summary,
        name='sales_summary'
    ),

    path(
        'top-products/',
        views.top_products,
        name='top_products'
    ),

    path(
        'customer-statement/',
        views.customer_statement_select,
        name='customer_statement_select'
    ),

    path(
        'customer-statement/<int:customer_id>/',
        views.customer_statement,
        name='customer_statement'
    ),
]
from django.urls import path
from core import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),

    path('customer-balance/', views.customer_balance, name='customer_balance'),
    path('sales-summary/', views.sales_summary, name='sales_summary'),
    path('top-products/', views.top_products, name='top_products'),

    path('customer-statement/select/', views.customer_statement_select, name='customer_statement_select'),
    path('customer-statement/<int:customer_id>/', views.customer_statement, name='customer_statement'),
]
