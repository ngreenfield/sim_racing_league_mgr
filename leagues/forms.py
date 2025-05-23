from django import forms
from .models import League

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['title', 'cars', 'tracks', 'race_day', 'race_time', 'image']