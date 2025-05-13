from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('summary/', views.attendance_summary, name='attendance_summary'),
    path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
    path('transfer-to-payroll/<int:summary_id>/', views.transfer_to_payroll, name='transfer_to_payroll'),
]