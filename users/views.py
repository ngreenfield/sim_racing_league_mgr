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


# Decorators - Updated to handle permission denied better
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        
        if not request.user.is_league_admin():
            messages.error(request, "Admin access required to perform this action.")
            return render(request, '403.html', {
                'error_message': 'Admin access required',
                'redirect_url': reverse_lazy('racer_dashboard')
            }, status=403)
        
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
    next_page = reverse_lazy('root')

# Admin Views
@login_required
@admin_required
def admin_dashboard(request):
    user = request.user

    # Leagues the admin has created
    leagues_created = League.objects.filter(created_by=user).order_by('-created_on')

    # Add registration info to each league the admin created
    for league in leagues_created:
        league.registered_users = league.participants.all()
        league.registration_count = league.participants.count()
        # Get recent registrations for this league
        league.recent_registrations = LeagueRegistration.objects.filter(
            league=league
        ).select_related('user').order_by('-registered_at')

    # Leagues the admin has registered for (avoiding duplicates)
    leagues_registered = League.objects.filter(
        leagueregistration__user=user
    ).order_by('-created_on').distinct()

    # All recent registrations across leagues the admin created
    all_recent_registrations = LeagueRegistration.objects.filter(
        league__created_by=user
    ).select_related('user', 'league').order_by('-registered_at')[:10]

    return render(request, 'users/admin/dashboard.html', {
        'leagues_created': leagues_created,
        'leagues_registered': leagues_registered,
        'all_recent_registrations': all_recent_registrations,
    })

# Racer Views - Updated to handle permission denied better
@login_required
def racer_dashboard(request):
    if not request.user.is_racer():
        messages.error(request, "Racer access required to view this page.")
        return render(request, '403.html', {
            'error_message': 'Racer access required',
            'redirect_url': reverse_lazy('login')
        }, status=403)
    
    # Get leagues where the user is not a participant
    available_leagues = League.objects.exclude(
        leagueregistration__user=request.user
    )
    
    # Get leagues the user has already registered for
    registered_leagues = request.user.joined_leagues.all()
    
    return render(request, 'users/racer/dashboard.html', {
        'available_leagues': available_leagues,
        'registered_leagues': registered_leagues,
    })

@login_required
def register_for_league(request, league_id):
    if not (request.user.is_racer() or request.user.is_league_admin()):
        messages.error(request, "You don't have permission to register for leagues.")
        return render(request, '403.html', {
            'error_message': 'Permission required to register for leagues',
            'redirect_url': reverse_lazy('login')
        }, status=403)
    
    league = get_object_or_404(League, id=league_id)
    
    LeagueRegistration.objects.get_or_create(
        user=request.user,
        league=league
    )
    
    messages.success(request, f'Registered for "{league.title}"!')
    
    if request.user.is_league_admin():
        return redirect('admin_dashboard')
    else:
        return redirect('racer_dashboard')


@login_required
def unregister_from_league(request, league_id):
    if not request.user.is_racer():
        messages.error(request, "Racer access required to unregister from leagues.")
        return render(request, '403.html', {
            'error_message': 'Racer access required',
            'redirect_url': reverse_lazy('login')
        }, status=403)
    
    league = get_object_or_404(League, id=league_id)
    registration = get_object_or_404(LeagueRegistration, user=request.user, league=league)
    
    registration.delete()
    messages.success(request, f'Unregistered from "{league.name}"!')
    return redirect('racer_dashboard')