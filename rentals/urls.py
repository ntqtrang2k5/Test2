from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='list'),
    path('tao-moi/', views.rental_create, name='create'),
    path('api/search-customers/', views.api_search_customers, name='search_customers'),
    path('api/search-cars/', views.api_search_cars, name='search_cars'),
    path('save-contract/', views.save_new_contract, name='save_contract'),
    path('save-customer/', views.save_customer, name='save_customer'),
    path('detail/<str:ma_hd>/', views.contract_detail, name='detail'),
]
