from django.shortcuts import render
from django.views.generic import ListView
from .models import Note

"""
Class-based views:
!MUST IMPORT!

View        = generic view
ListView    = get a list of records
DetailView  = get a single(detail) record
CreateView  = create a new record
DeleteView  = remove a record
UpdateView  = modify an existing record
LoginView   = login
"""


# Create your views here.
class NoteList(ListView):
    model = Note
    template_name = 'notes/list.html'