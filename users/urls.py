from django.urls import path
from . import views


urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Racer
    path('racer/dashboard/', views.racer_dashboard, name='racer_dashboard'),
    path('leagues/<int:league_id>/register/', views.register_for_league, name='register_for_league'),
    path('leagues/<int:league_id>/unregister/', views.unregister_from_league, name='unregister_from_league'),
]