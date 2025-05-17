from django.urls import path
from pages import views


urlpatterns = [
    path('', views.home_view, name="root"),
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact')
]