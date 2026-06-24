from django.urls import path

from . import views

app_name = 'regions'

urlpatterns = [
    path('api/locations/provinces/', views.api_provinces, name='api_provinces'),
    path('api/locations/cities/', views.api_cities, name='api_cities'),
    path('api/locations/districts/', views.api_districts, name='api_districts'),
    path('api/locations/postal-code/', views.api_postal_code, name='api_postal_code'),
]
