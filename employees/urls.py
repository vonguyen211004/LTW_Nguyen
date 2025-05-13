from django.urls import path
from . import views

urlpatterns = [
	path('', views.employee_list, name='employee_list'),
	path('<int:pk>/', views.employee_detail, name='employee_detail'),
	path('create/', views.employee_create, name='employee_create'),
	path('update/<int:pk>/', views.employee_update, name='employee_update'),
	path('delete/<int:pk>/', views.employee_delete, name='employee_delete'),

	# Quản lý người phụ thuộc
	path('dependent/create/<int:employee_id>/', views.dependent_create, name='dependent_create'),
	path('dependent/update/<int:pk>/', views.dependent_update, name='dependent_update'),
	path('dependent/delete/<int:pk>/', views.dependent_delete, name='dependent_delete'),

	# Quản lý kỷ luật
	path('discipline/create/<int:employee_id>/', views.discipline_create, name='discipline_create'),
	path('discipline/update/<int:pk>/', views.discipline_update, name='discipline_update'),
	path('discipline/delete/<int:pk>/', views.discipline_delete, name='discipline_delete'),

	# Quản lý khen thưởng
	path('reward/create/<int:employee_id>/', views.reward_create, name='reward_create'),
	path('reward/update/<int:pk>/', views.reward_update, name='reward_update'),
	path('reward/delete/<int:pk>/', views.reward_delete, name='reward_delete'),

	# API
	path('api/calculate-tax/<int:employee_id>/', views.calculate_tax_api, name='calculate_tax_api'),
]