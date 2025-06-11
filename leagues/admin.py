
from django.contrib import admin
from .models import League, Track, Car, LeagueRegistration, Race, RaceResult, ChampionshipStanding

# Customizing League Admin to include participant count
@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['title', 'participant_count', 'race_day', 'race_time', 'created_on']
    filter_horizontal = ['cars',]  # Makes selecting cars/tracks easier

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Number of Participants'

# Registering Track and Car models without any changes
admin.site.register(Track)
admin.site.register(Car)

# Add the new race-related models

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'track', 'race_date', 'is_completed', 'participants_count']
    list_filter = ['league', 'is_completed', 'race_date']
    search_fields = ['name']

@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ['race', 'driver', 'position', 'points', 'dnf']
    list_filter = ['race', 'dnf']
    search_fields = ['driver__username', 'race__name']
    ordering = ['race', 'position']

@admin.register(ChampionshipStanding)
class ChampionshipStandingAdmin(admin.ModelAdmin):
    list_display = ['driver', 'league', 'total_points', 'wins', 'podiums', 'races_participated']
    list_filter = ['league']
    search_fields = ['driver__username']
    ordering = ['-total_points']

