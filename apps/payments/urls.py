from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('finish/<int:order_id>/', views.payment_finish, name='finish'),
    path('unfinish/<int:order_id>/', views.payment_unfinish, name='unfinish'),
    path('error/<int:order_id>/', views.payment_error, name='error'),
    path('notification/', views.payment_notification, name='notification'),
]
