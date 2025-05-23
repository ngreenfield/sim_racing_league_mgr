from django.db import models

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
    cars = models.ManyToManyField(Car, related_name='leagues')
    tracks = models.ManyToManyField(Track, related_name='leagues')
    race_day = models.CharField(max_length=78)
    race_time = models.TimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="leagues/", blank=True, null=True)

    def __str__(self):
        return self.title

    
