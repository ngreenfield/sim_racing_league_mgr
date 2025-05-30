from functools import wraps
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import User
from leagues.models import League, LeagueRegistration
from leagues.forms import LeagueForm


# Decorators
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_league_admin():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


# Registration Form
class RacerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'racer'
        if commit:
            user.save()
        return user


# Authentication
def register_view(request):
    if request.method == 'POST':
        form = RacerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('racer_dashboard')
    else:
        form = RacerRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'  

    def get_success_url(self):
        if self.request.user.is_league_admin():
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('racer_dashboard')
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

# Admin Views
@login_required
@admin_required
def admin_dashboard(request):
    leagues = League.objects.all().order_by('-created_on')
    return render(request, 'users/admin/dashboard.html', {'leagues': leagues})


@login_required
@admin_required
def create_league(request):
    if request.method == 'POST':
        form = LeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            league.created_by = request.user
            league.save()
            messages.success(request, f'League "{league.name}" created!')
            return redirect('admin_dashboard')
    else:
        form = LeagueForm()
    return render(request, 'admin/create_league.html', {'form': form})


@login_required
@admin_required
def delete_league(request, league_id):
    league = get_object_or_404(League, id=league_id)
    if request.method == 'POST':
        league.delete()
        messages.success(request, 'League deleted!')
        return redirect('admin_dashboard')
    return render(request, 'admin/delete_league.html', {'league': league})


# Racer Views
@login_required
def racer_dashboard(request):
    if not request.user.is_racer():
        raise PermissionDenied
    
    available_leagues = League.objects.exclude(participants=request.user)
    registered_leagues = request.user.joined_leagues.all()
    
    return render(request, 'racer/dashboard.html', {
        'available_leagues': available_leagues,
        'registered_leagues': registered_leagues,
    })


@login_required
def register_for_league(request, league_id):
    if not request.user.is_racer():
        raise PermissionDenied
    
    league = get_object_or_404(League, id=league_id)
    
    LeagueRegistration.objects.get_or_create(
        user=request.user,
        league=league
    )
    
    messages.success(request, f'Registered for "{league.name}"!')
    return redirect('racer_dashboard')


@login_required
def unregister_from_league(request, league_id):
    if not request.user.is_racer():
        raise PermissionDenied
    
    league = get_object_or_404(League, id=league_id)
    registration = get_object_or_404(LeagueRegistration, user=request.user, league=league)
    
    registration.delete()
    messages.success(request, f'Unregistered from "{league.name}"!')
    return redirect('racer_dashboard')