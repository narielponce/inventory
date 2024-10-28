# urls.py

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('income/new/', views.create_income, name='create_income'),
    path('outcome/new/', views.create_outcome, name='create_outcome'),
    path('inventory/', views.inventory_list, name='inventory_list'), # ruta para listar el inventario
    path('transaction/', views.transaction_list, name='transaction_list'),
    path('generate-inventory-pdf/', views.generate_inventory_pdf, name='generate_inventory_pdf'),
    path('generate-inventory-xls/', views.generate_inventory_xls, name='generate_inventory_xls'),
]
