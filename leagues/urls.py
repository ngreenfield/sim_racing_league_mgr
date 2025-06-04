from django.urls import path
from . import views

urlpatterns=[
    path('list/', views.LeagueList.as_view(), name="league_list"),
    path('create/', views.LeagueCreate.as_view(), name="league_create"),
    path('details/<int:pk>/', views.LeagueDetail.as_view(), name="league_details"),
    path('update/<int:pk>/', views.LeagueUpdate.as_view(), name="league_update"),
    path('delete/<int:pk>', views.LeagueDelete.as_view(), name="league_delete"),
    path('register/<int:pk>/', views.register_for_league, name="register_for_league"),
]

