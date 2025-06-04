from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import League, LeagueRegistration
from .forms import LeagueForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirect to your actual login URL
            from django.shortcuts import redirect
            login_url = '/users/login/'  # Direct path to your login
            return redirect(f"{login_url}?next={request.get_full_path()}")
        
        if not hasattr(request.user, 'is_league_admin') or not request.user.is_league_admin():
            # Custom permission denied message
            messages.error(request, "You don't have permission to access this page. Admin access required.")
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Admin access required.")
        
        return super().dispatch(request, *args, **kwargs)

# Create your views here.
class LeagueList(ListView):
    model = League
    template_name = 'leagues/list.html'


class LeagueCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = League
    form_class = LeagueForm
    template_name = "leagues/create.html"
    success_url = reverse_lazy('league_list')

    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create League"
        return context


class LeagueDetail(DetailView):
    model = League
    template_name = "leagues/details.html"


class LeagueUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = League
    form_class = LeagueForm
    template_name = "leagues/create.html"
    success_url = reverse_lazy("league_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update League"
        return context
    

class LeagueDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = League
    template_name = "leagues/delete.html"
    success_url = reverse_lazy('league_list')


@login_required
def register_for_league(request, pk):
    league = get_object_or_404(League, pk=pk)

    # Check if the user is already registered for the league
    if LeagueRegistration.objects.filter(user=request.user, league=league).exists():
        messages.error(request, "You are already registered for this league.")
        return render(request, '403.html', {
            'error_message': 'You are already registered for this league',
            'redirect_url': reverse_lazy('league_detail', kwargs={'pk': pk})
        }, status=403)
    
    # Check if the league is full (only if max_participants field exists)
    if hasattr(league, 'max_participants') and league.max_participants:
        if league.participants.count() >= league.max_participants:
            messages.error(request, "This league is full and cannot accept more registrations.")
            return render(request, '403.html', {
                'error_message': 'This league is full',
                'redirect_url': reverse_lazy('league_detail', kwargs={'pk': pk})
            }, status=403)
    
    # Register the user for the league
    LeagueRegistration.objects.create(user=request.user, league=league)
    
    # Use the correct field name (change 'title' to 'name' if needed)
    league_name = getattr(league, 'name', getattr(league, 'title', 'the league'))
    messages.success(request, f"You've successfully registered for {league_name}!")
    return redirect('league_detail', pk=pk)


@login_required 
def unregister_from_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    
    try:
        registration = LeagueRegistration.objects.get(user=request.user, league=league)
        registration.delete()
        
        league_name = getattr(league, 'name', getattr(league, 'title', 'the league'))
        messages.success(request, f'Unregistered from "{league_name}"!')
        
    except LeagueRegistration.DoesNotExist:
        messages.error(request, "You are not registered for this league.")
    
    return redirect('league_detail', pk=pk)