from django.urls import path
from . import views

urlpatterns =[
    path('list/', views.NoteList.as_view(), name="note_list")
]