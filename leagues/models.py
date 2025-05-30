from django.db import models
from django.conf import settings

# Create your models here.
class Track(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="tracks/", blank=True, null=True)

    def __str__(self):
        return self.name
    
class Car(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cars/", blank=True, null=True)

    def __str__(self):
        return self.name
    
class League(models.Model):
    title = models.CharField(max_length=100)
    cars = models.ManyToManyField('Car', related_name='leagues')
    tracks = models.ManyToManyField('Track', related_name='leagues')
    race_day = models.CharField(max_length=78)
    race_time = models.TimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="leagues/", blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='LeagueRegistration', related_name='joined_leagues')

    def __str__(self):
        return self.title


class LeagueRegistration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'league')

    def __str__(self):
        return f"{self.user.username} registered for {self.league.title}"