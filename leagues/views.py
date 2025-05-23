from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import League
from .forms import LeagueForm
from django.urls import reverse_lazy

# Create your views here.
class LeagueList(ListView):
    model = League
    template_name = 'leagues/list.html'


class LeagueCreate(CreateView):
    model = League
    form_class = LeagueForm
    template_name = "leagues/create.html"
    success_url = reverse_lazy('league_list')