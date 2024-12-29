from django.db import models
from django.contrib.auth.models import User
from quiz_app.models import Species

class AestheticChoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    image_filename = models.CharField(max_length=255, default='default_image.jpg')
    chosen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'species', 'image_filename')

    def __str__(self):
        return f"{self.user.username} chose {self.species.name}"