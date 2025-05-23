from django.urls import path
from . import views

urlpatterns=[
    path('list/', views.LeagueList.as_view(), name="league_list"),
    path('create/', views.LeagueCreate.as_view(), name="league_create"),
]