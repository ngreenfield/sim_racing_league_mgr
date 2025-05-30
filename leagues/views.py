from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import League, LeagueRegistration
from .forms import LeagueForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class LeagueList(ListView):
    model = League
    template_name = 'leagues/list.html'


class LeagueCreate(CreateView, LoginRequiredMixin):
    model = League
    form_class = LeagueForm
    template_name = "leagues/create.html"
    success_url = reverse_lazy('league_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create League"
        return context


class LeagueDetail(DetailView, LoginRequiredMixin):
    model = League
    template_name = "leagues/details.html"


class LeagueUpdate(UpdateView, LoginRequiredMixin):
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


@login_required
def register_for_league(request, pk):
    league = get_object_or_404(League, pk=pk)

    # Check if the user is already registered for the league
    if LeagueRegistration.objects.filter(user=request.user, league=league).exists():
        raise PermissionDenied("You are already registered for this league.")
    
    # Check if the league is full (if you choose to implement a max participant count)
    if league.participants.count() >= league.max_participants:
        raise PermissionDenied("This league is full and cannot accept more registrations.")
    
    # Register the user for the league
    LeagueRegistration.objects.create(user=request.user, league=league)
    
    messages.success(request, f"You've successfully registered for {league.title}!")
    return redirect('league_details', pk=pk)
