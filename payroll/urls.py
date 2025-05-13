from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_list, name='payroll_list'),
    path('<int:pk>/', views.payroll_detail, name='payroll_detail'),
    path('employee/<int:payroll_id>/<int:detail_id>/', views.payroll_employee_detail, name='payroll_employee_detail'),
    path('disable/<int:pk>/', views.disable_payroll, name='disable_payroll'),
    path('activate/<int:pk>/', views.activate_payroll, name='activate_payroll'),
    path('approve/<int:pk>/', views.approve_payroll, name='approve_payroll'),
    path('mark-as-paid/<int:pk>/', views.mark_as_paid, name='mark_as_paid'),
    path('export-excel/<int:pk>/', views.export_payroll_excel, name='export_payroll_excel'),
]