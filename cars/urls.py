from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.car_list, name='list'),
    path('config/save/', views.config_save, name='config_save'),
    path('config/delete/', views.config_delete, name='config_delete'),
    
    path('add/', views.car_form, name='add'),
    path('edit/<str:bien_so>/', views.car_form, name='edit'),
    path('save/', views.car_save, name='save'),
    path('delete/', views.car_delete, name='car_delete'),

    path('expense/save/', views.expense_save, name='expense_save'),
    path('expense/delete/', views.expense_delete, name='expense_delete'),
]


