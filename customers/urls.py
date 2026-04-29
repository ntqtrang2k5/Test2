from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='list'),
    path('save/', views.save_customer, name='save'),
    path('delete/', views.delete_customer, name='delete'),
    path('history/<str:ma_kh>/', views.customer_history, name='history'),
]
