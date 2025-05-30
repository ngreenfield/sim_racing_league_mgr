from django.contrib.auth.models import AbstractUser
from django.db import models
from leagues.models import League

class User(AbstractUser):
    ROLE_CHOICES = (
        ('racer', 'Racer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='racer')

    def is_racer(self):
        return self.role == 'racer'

    def is_league_admin(self):
        return self.role == 'admin'

    @property
    def joined_leagues(self):
        return League.objects.filter(leagueregistration__user=self)