from django.urls import path
from . import views
from . import reviews as review_views

app_name = 'products'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about-morris/', views.AboutView.as_view(), name='about'),
    path('fragrance-guide/', views.FragranceGuideView.as_view(), name='fragrance_guide'),
    path('products/', views.ProductListView.as_view(), name='list'),
    path('products/note/<slug:slug>/', views.ProductByNoteView.as_view(), name='by_note'),
    path('products/family/<slug:slug>/', views.ProductByFamilyView.as_view(), name='by_family'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('products/<slug:slug>/review/', review_views.ReviewFormView.as_view(), name='review_form'),
    path('review/<int:pk>/delete/', review_views.ReviewDeleteView.as_view(), name='review_delete'),
]
