from django.urls import path
from . import views

urlpatterns = [
	# Trang chủ chấm công
	path('', views.dashboard, name='attendance_dashboard'),

	# Tổng hợp chấm công
	path('summary/', views.attendance_summary, name='attendance_summary'),
	path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
	path('summary/transfer-to-payroll/<int:summary_id>/', views.transfer_to_payroll, name='transfer_to_payroll'),



	path('work-shifts/', views.work_shift_list, name='work_shift_list'),
	path('work-shifts/add/', views.work_shift_form, name='work_shift_form'),
	path('work-shifts/edit/<int:id>/', views.work_shift_form, name='work_shift_form'),
	path('work-shifts/detail/<int:id>/', views.work_shift_detail, name='work_shift_detail'),
	path('work-shifts/delete/<int:id>/', views.work_shift_delete, name='work_shift_delete'),


	path('attendance-details/', views.attendance_detail_list, name='attendance_detail_list'),
	path('attendance-details/add/', views.attendance_detail_form, name='attendance_detail_form'),
	path('attendance-details/edit/<int:id>/', views.attendance_detail_form, name='attendance_detail_form'),
	path('attendance-details/delete/<int:id>/', views.attendance_detail_delete, name='attendance_detail_delete'),
	path('attendance-details/view/<int:id>/', views.attendance_detail_view, name='attendance_detail_view'),
	path('attendance-details/update/<int:record_id>/<int:employee_id>/<str:date_str>/', views.update_daily_attendance, name='update_daily_attendance'),
	path('attendance-details/get/<int:record_id>/<int:employee_id>/<str:date_str>/', views.get_daily_attendance, name='get_daily_attendance'),
path('attendance-detail-save/', views.attendance_detail_save, name='attendance_detail_save'),

	path('summary/add/', views.attendance_summary_form, name='attendance_summary_form'),
	path('summary/edit/<int:id>/', views.attendance_summary_form, name='attendance_summary_form'),
	path('summary/delete/<int:id>/', views.attendance_summary_delete, name='attendance_summary_delete'),

	# URL cho bảng chấm công tổng hợp
	path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
	path('summary/<int:id>/delete/', views.attendance_summary_delete, name='attendance_summary_delete'),

	# URL cho chức năng chuyển tính lương
	path('summary/<int:summary_id>/transfer/', views.transfer_to_payroll, name='transfer_to_payroll'),
	# URL cho bảng chấm công tổng hợp

	path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
	path('summary/<int:id>/delete/', views.attendance_summary_delete, name='attendance_summary_delete'),

	# URL cho chức năng chuyển tính lương
	path('summary/<int:summary_id>/transfer/', views.transfer_to_payroll, name='transfer_to_payroll'),

	path('summary/', views.attendance_list, name='attendance_list'),  # Tên URL pattern đã được thay đổi
	path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
	path('summary/<int:id>/edit/', views.attendance_summary_edit, name='attendance_summary_edit'),
	path('summary/<int:id>/delete/', views.attendance_summary_delete, name='attendance_summary_delete'),

	# URL cho chức năng chuyển tính lương
	path('summary/<int:summary_id>/transfer/', views.transfer_to_payroll, name='transfer_to_payroll'),
]