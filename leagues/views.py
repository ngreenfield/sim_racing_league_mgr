from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create League"
        return context


class LeagueDetail(DetailView):
    model = League
    template_name = "leagues/details.html"


class LeagueUpdate(UpdateView):
    model = League
    form_class = LeagueForm
    template_name = "leagues/create.html"
    success_url = reverse_lazy("league_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update League"
        return context
    

class LeagueDelete(DeleteView):
    model = League
    template_name = "leagues/delete.html"
    success_url = reverse_lazy('league_list')