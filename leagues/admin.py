from django.contrib import admin
from .models import League, Track, Car

# Customizing League Admin to include participant count
@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['title', 'participant_count', 'race_day', 'race_time', 'created_on']

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Number of Participants'

# Registering Track and Car models without any changes
admin.site.register(Track)
admin.site.register(Car)