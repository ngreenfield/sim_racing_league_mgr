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
    race_day = models.CharField(max_length=78)
    race_time = models.TimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="leagues/", blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=20)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leagues_created',
        null=True,  # Only if you're adding this after leagues already exist
        blank=True
    )

    def __str__(self):
        return self.title

    @property
    def participants(self):
        """Get all users registered for this league"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(leagueregistration__league=self)


class LeagueRegistration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'league')

    def __str__(self):
        return f"{self.user.username} registered for {self.league.title}"


class Race(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='races')
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    race_date = models.DateTimeField()
    laps = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    weather_conditions = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-race_date']
    
    def __str__(self):
        return f"{self.name} - {self.league.title}"
    
    @property
    def participants_count(self):
        return self.results.count()


##### RACE RESULTS #####
class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='results')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    position = models.PositiveIntegerField()
    fastest_lap_time = models.CharField(max_length=20, blank=True, help_text="Format: MM:SS.mmm")
    laps_completed = models.PositiveIntegerField(default=0)
    dnf = models.BooleanField(default=False, verbose_name="Did Not Finish")
    points = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('race', 'driver')
        ordering = ['position']
    
    def __str__(self):
        return f"{self.race.name} - {self.driver.username} (P{self.position})"


class ChampionshipStanding(models.Model):
    """Track championship points across a league season"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='standings')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    races_participated = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    podiums = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('league', 'driver')
        ordering = ['-total_points', '-wins', '-podiums']
    
    def __str__(self):
        return f"{self.driver.username} - {self.league.title} ({self.total_points} pts)"