from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('create/', views.order_create, name='create'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('<int:order_id>/cancel/', views.order_cancel, name='cancel'),
    path('<int:order_id>/confirm-received/', views.order_confirm_received, name='confirm_received'),
    path('<int:order_id>/track/', views.order_track, name='track'),
]
