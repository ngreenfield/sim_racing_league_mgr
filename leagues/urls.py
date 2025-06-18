from django.urls import path
from . import views

urlpatterns=[
    path('list/', views.LeagueList.as_view(), name="league_list"),
    path('create/', views.LeagueCreate.as_view(), name="league_create"),
    path('details/<int:pk>/', views.LeagueDetail.as_view(), name="league_details"),
    path('update/<int:pk>/', views.LeagueUpdate.as_view(), name="league_update"),
    path('delete/<int:pk>', views.LeagueDelete.as_view(), name="league_delete"),
    path('register/<int:pk>/', views.register_for_league, name="register_for_league"),

     # Race URLs
    path('races/', views.RaceListView.as_view(), name='race_list'),
    path('races/<int:pk>/', views.RaceDetailView.as_view(), name='race_details'),
    path('races/create/', views.RaceCreateView.as_view(), name='race_create'),
    path('races/<int:race_id>/results/', views.RaceResultsCreateView.as_view(), name='race_results'),
    path('races/add/', views.add_race, name='add_race'),
    
    # League standings
    path('leagues/<int:pk>/standings/', views.LeagueStandingsView.as_view(), name='league_standings'),
]

