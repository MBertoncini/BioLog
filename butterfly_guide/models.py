from django.db import models
from django.contrib.auth.models import User

class ButterflySpecies(models.Model):
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='butterflies/')
    habitat = models.CharField(max_length=100)
    season = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Observation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(ButterflySpecies, on_delete=models.CASCADE)
    date = models.DateField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='observations/')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.species.name} observed by {self.user.username}"