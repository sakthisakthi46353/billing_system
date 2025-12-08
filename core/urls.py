from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reports/', views.reports_home, name='reports_home'),
    path('reports/customer-balance/', views.customer_balance, name='customer_balance'),
    path('reports/sales-summary/', views.sales_summary, name='sales_summary'),
    path('reports/top-products/', views.top_products, name='top_products'),
    path('reports/customer-statement/', views.customer_statement, name='customer_statement'),
    path('reports/customer-balance/', views.customer_balance, name='customer_balance'),
    path('reports/customer-statement/<int:customer_id>/', views.customer_statement, name='customer_statement'),
    path('reports/customer-statement/<int:customer_id>/', views.customer_statement, name='customer_statement'),

]
