from django.urls import path
from . import views

urlpatterns = [
    path('', views.personnel_overview, name='personnel_overview'),
    path('ho-so/', views.personnel_list, name='personnel_list'),
    path('ho-so/<int:pk>/', views.personnel_detail, name='personnel_detail'),
    path('ho-so/them/', views.personnel_create, name='personnel_create'),
]
