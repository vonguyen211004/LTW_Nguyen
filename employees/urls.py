from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    # Employee URLs
    path('', views.employee_list, name='employee_list'),
    path('them/', views.employee_create, name='employee_create'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/cap-nhat/', views.employee_update, name='employee_update'),
    path('<int:pk>/vo-hieu-hoa/', views.employee_deactivate, name='employee_deactivate'),
    path('<int:pk>/kich-hoat/', views.employee_activate, name='employee_activate'),

    # Personnel URLs
    path('tong-quan/', views.personnel_overview, name='personnel_overview'),
    path('ho-so/', views.personnel_profile, name='personnel_profile'),


# employees/urls.py

]