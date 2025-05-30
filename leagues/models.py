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


class LeagueRegistration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'league')

    def __str__(self):
        return f"{self.user.username} registered for {self.league.title}"