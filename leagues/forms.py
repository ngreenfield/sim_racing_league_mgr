from django import forms
from .models import League, RaceResult, LeagueRegistration, Race
from django.contrib.auth import get_user_model

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['title', 'cars', 'race_day', 'race_time',  'max_participants', 'image']

class RaceResultForm(forms.ModelForm):
    class Meta:
        model = RaceResult
        fields = ['driver', 'position', 'fastest_lap_time', 'laps_completed', 'points', 'dnf']

    driver = forms.ModelChoiceField(queryset=None, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        race = kwargs.pop('race', None)  # Get the race object from the view or form initialization
        super().__init__(*args, **kwargs)

        if race:
            # Filter drivers by league registration for the race's league
            registered_drivers = LeagueRegistration.objects.filter(league=race.league).values_list('user', flat=True)
            self.fields['driver'].queryset = get_user_model().objects.filter(id__in=registered_drivers)

class AddRaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ['league', 'track', 'name', 'race_date', 'laps', 'weather_conditions']