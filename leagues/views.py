from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, FormView
from .models import League, LeagueRegistration, Race, RaceResult, ChampionshipStanding
from .forms import LeagueForm, RaceResultForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth import get_user_model

User = get_user_model()


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


#### RACE RESULTS ####
class RaceListView(ListView):
    model = Race
    template_name = 'races/race_list.html'
    context_object_name = 'races'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Race.objects.select_related('league', 'track').prefetch_related('results')
        
        # Filter by league if provided
        league_id = self.request.GET.get('league')
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        # Filter by completion status
        completed = self.request.GET.get('completed')
        if completed == 'true':
            queryset = queryset.filter(is_completed=True)
        elif completed == 'false':
            queryset = queryset.filter(is_completed=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leagues'] = League.objects.all()
        context['selected_league'] = self.request.GET.get('league')
        context['completed_filter'] = self.request.GET.get('completed')
        return context


class RaceDetailView(DetailView):
    model = Race
    template_name = 'races/race_detail.html'
    context_object_name = 'race'
    
    def get_queryset(self):
        return Race.objects.select_related('league', 'track').prefetch_related(
            'results__driver', 'results__car'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.get_object()
        
        # Get race results ordered by position
        results = race.results.select_related('driver', 'car').order_by('position')
        context['results'] = results
        
        # Calculate race statistics
        if results.exists():
            context['total_drivers'] = results.count()
            context['dnf_count'] = results.filter(dnf=True).count()
            context['finishers'] = results.filter(dnf=False).count()
            
            # Get fastest lap info
            fastest_lap_result = results.exclude(fastest_lap_time='').exclude(fastest_lap_time__isnull=True).first()
            if fastest_lap_result:
                context['fastest_lap_driver'] = fastest_lap_result.driver
                context['fastest_lap_time'] = fastest_lap_result.fastest_lap_time
        
        return context


class LeagueStandingsView(DetailView):
    model = League
    template_name = 'leagues/standings.html'
    context_object_name = 'league'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = self.get_object()
        
        # Get championship standings
        standings = ChampionshipStanding.objects.filter(
            league=league
        ).select_related('driver').order_by('-total_points', '-wins', '-podiums')
        
        context['standings'] = standings
        
        # Get recent races for this league
        recent_races = Race.objects.filter(
            league=league, 
            is_completed=True
        ).order_by('-race_date')[:5]
        
        context['recent_races'] = recent_races
        
        return context


class RaceCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Race
    fields = ['league', 'track', 'name', 'race_date', 'laps', 'weather_conditions', 'race_length_minutes']
    template_name = 'races/race_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Race'
        return context
    
    def get_success_url(self):
        return reverse_lazy('race_detail', kwargs={'pk': self.object.pk})


POINTS_SYSTEM = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1
}

def calculate_points(position, dnf=False):
    if dnf:
        return 0
    return POINTS_SYSTEM.get(position, 0)


class RaceResultsCreateView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    model = Race
    template_name = 'races/add_results.html'
    context_object_name = 'race'
    form_class = RaceResultForm
    
    # Override to use the race_id from URL
    def get_object(self, queryset=None):
        # Get the race object by its pk from the URL (race_id)
        race_id = self.kwargs.get('race_id')
        return get_object_or_404(Race, pk=race_id)
    
    def get_formset(self, race, extra=0):
        """Factory method to create a formset for the race results."""
        RaceResultFormSet = modelformset_factory(
            RaceResult,
            fields=['driver', 'car', 'position', 'fastest_lap_time', 
                    'laps_completed', 'dnf'],
            extra=extra,
            can_delete=True
        )
        # Pre-populate with existing results or empty forms
        existing_results = race.results.all()
        if existing_results.exists():
            return RaceResultFormSet(queryset=existing_results)
        else:
            return RaceResultFormSet(queryset=RaceResult.objects.none())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.get_object()
        
        # Get all registered drivers for this league
        registered_drivers = race.league.participants.all()
        
        # Create the formset
        formset = self.get_formset(race, extra=registered_drivers.count())
        
        context['formset'] = formset
        context['registered_drivers'] = registered_drivers
        context['available_cars'] = race.league.cars.all()
        
        return context
    
    def post(self, request, *args, **kwargs):
        race = self.get_object()
        
        formset = self.get_formset(race)
        
        if formset.is_valid():
            with transaction.atomic():
                # Clear existing results for this race
                race.results.all().delete()
                
                # Save new results
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        result = form.save(commit=False)
                        result.race = race
                        
                        result.points = calculate_points(
                            result.position, 
                            result.dnf
                        )
                        
                        result.save()
                
                # Mark race as completed
                race.is_completed = True
                race.save()
                
                # Update championship standings
                update_championship_standings(race)
                
                messages.success(request, f'Race results for {race.name} have been saved successfully!')
                return redirect('race_detail', pk=race.pk)
        
        # If formset is not valid, re-render with errors
        context = self.get_context_data()
        context['formset'] = formset
        return render(request, self.template_name, context)

class RaceResultsUpdateView(LoginRequiredMixin, AdminRequiredMixin, DetailView, FormView):
    model = Race
    template_name = 'races/update_results.html'
    context_object_name = 'race'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.get_object()
        
        context['race'] = race
        
        # Get all registered drivers for this league
        registered_drivers = race.league.participants.all()
        
        # Create the formset
        formset = self.get_formset(race, extra=registered_drivers.count())
        
        context['formset'] = formset
        context['registered_drivers'] = registered_drivers
        context['available_cars'] = race.league.cars.all()
        
        return context
    
    def post(self, request, *args, **kwargs):
        race = self.get_object()
        
        RaceResultInlineFormSet = inlineformset_factory(
            Race,
            RaceResult,
            fields=['driver', 'car', 'position', 'fastest_lap_time', 'total_time', 
                   'laps_completed', 'dnf', 'dnf_reason'],
            extra=0,
            can_delete=True
        )
        
        formset = RaceResultInlineFormSet(request.POST, instance=race)
        
        if formset.is_valid():
            with transaction.atomic():
                # Save the formset
                instances = formset.save(commit=False)
                
                # Calculate points for each result
                for result in instances:
                    result.points = calculate_points(result.position, result.dnf)
                    result.save()
                
                # Handle deletions
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Update championship standings
                update_championship_standings(race)
                
                messages.success(request, f'Race results for {race.name} have been updated successfully!')
                return redirect('race_detail', pk=race.pk)
        
        # If form is not valid, re-render with errors
        context = self.get_context_data()
        context['formset'] = formset
        return render(request, self.template_name, context)
    

def update_championship_standings(race):
    # Get all drivers who have participated in this league
    league_drivers = User.objects.filter(
        raceresult__race__league=race.league
    ).distinct()
    
    for driver in league_drivers:
        standing, created = ChampionshipStanding.objects.get_or_create(
            league=race.league,
            driver=driver,
            defaults={
                'total_points': 0,
                'races_participated': 0,
                'wins': 0,
                'podiums': 0
            }
        )
        
        all_results = RaceResult.objects.filter(
            race__league=race.league,
            driver=driver,
            race__is_completed=True
        )
        
        standing.total_points = sum(r.points for r in all_results)
        standing.races_participated = all_results.count()
        standing.wins = all_results.filter(position=1).count()
        standing.podiums = all_results.filter(position__lte=3).count()
        standing.save()


class RaceResultsDeleteView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Race
    template_name = 'races/delete_results.html'
    context_object_name = 'race'
    
    def post(self, request, *args, **kwargs):
        race = self.get_object()
        
        with transaction.atomic():
            # Delete all results for this race
            race.results.all().delete()
            
            # Mark race as not completed
            race.is_completed = False
            race.save()
            
            update_all_league_standings(race.league)
            
            messages.success(request, f'All results for {race.name} have been deleted.')
            return redirect('race_detail', pk=race.pk)
        
        return self.get(request, *args, **kwargs)


def update_all_league_standings(league):
    # Clear existing standings
    ChampionshipStanding.objects.filter(league=league).delete()
    
    # Get all completed races for this league
    completed_races = Race.objects.filter(league=league, is_completed=True)
    
    for race in completed_races:
        update_championship_standings(race)