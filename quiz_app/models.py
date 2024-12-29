from django.db import models
from django.contrib.auth.models import User
from .image_utils import resize_image
from django.db.models import Count


class Species(models.Model):
    name = models.CharField(max_length=200, unique=True)
    family = models.CharField(max_length=200)
    probability = models.FloatField()
    times_shown = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Species"

class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Month(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class SpeciesAreaWeight(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    weight = models.FloatField()

    class Meta:
        unique_together = ('species', 'region')
    
    def __str__(self):
        return f"{self.species.name} - {self.region.name}: {self.weight}"

class SpeciesPeriodWeight(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    weight = models.FloatField()

    class Meta:
        unique_together = ('species', 'month')
    
    def __str__(self):
        return f"{self.species.name} - {self.month.name}: {self.weight}"

class Question(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    image_url = models.URLField()
    observation_url = models.URLField()
    license_code = models.CharField(max_length=50)
    attribution = models.CharField(max_length=200)
    observed_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Question about {self.species.name}"
from django.db import models
from django.contrib.auth.models import User


class Observation(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    inaturalist_id = models.IntegerField(unique=True)
    observed_on = models.DateField()
    url = models.URLField()
    times_shown = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)

    def __str__(self):
        return f"Observation {self.inaturalist_id} of {self.species.name}"

class Image(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    url = models.URLField()
    license_code = models.CharField(max_length=50)
    attribution = models.CharField(max_length=200)
    times_shown = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)

    def __str__(self):
        return f"Image for {self.observation}"

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
#email_confirmed = models.BooleanField(default=False)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar = models.ImageField(upload_to='profile_avatars/', null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    species_observation_history = models.JSONField(default=dict)
    difficult_species = models.JSONField(default=dict)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    birth_date = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username

    def update_stats(self):
        from quiz_app.models import QuizQuestion
        stats = QuizQuestion.objects.filter(quiz_session__user=self.user).aggregate(
            total_questions=models.Count('id'),
            correct_answers=models.Sum('is_correct')
        )
        self.total_questions = stats['total_questions'] or 0
        self.correct_answers = stats['correct_answers'] or 0
        self.save()

    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
        else:
            instance.userprofile.save()

    def update_stats(self):
            from quiz_app.models import QuizQuestion
            stats = QuizQuestion.objects.filter(quiz_session__user=self.user).aggregate(
                total_questions=models.Count('id'),
                correct_answers=models.Sum('is_correct')
            )
            self.total_questions = stats['total_questions'] or 0
            self.correct_answers = stats['correct_answers'] or 0
            self.save()

    difficult_species = models.JSONField(default=dict)

    def update_difficult_species(self):
        from quiz_app.models import UserIncorrectAnswer
        difficult_species = UserIncorrectAnswer.objects.filter(user=self.user) \
            .values('species__name') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:5]
        
        self.difficult_species = {item['species__name']: item['count'] for item in difficult_species}
        self.save()



class UserIncorrectAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    quiz_session = models.ForeignKey('QuizSession', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Incorrect answer by {self.user.username} for {self.species.name}"

    def update_stats(self):
        from quiz_app.models import QuizQuestion
        stats = QuizQuestion.objects.filter(quiz_session__user=self.user).aggregate(
            total_questions=models.Count('id'),
            correct_answers=models.Sum('is_correct')
        )
        self.total_questions = stats['total_questions'] or 0
        self.correct_answers = stats['correct_answers'] or 0
        self.save()



class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)  # Cambiato da IntegerField a FloatField
    total_questions = models.IntegerField(default=10)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    month = models.ForeignKey(Month, on_delete=models.SET_NULL, null=True)
    quiz_type = models.CharField(max_length=20, choices=[('multiple_choice', 'Scelta Multipla'), ('text_input', 'Inserimento Testo')])
    user_answer = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, related_name='quiz_session_answers')


    def __str__(self):
        return f"Quiz session for {self.user.username} on {self.start_time}"

    @property
    def questions(self):
        return self.questions.all().order_by('question_number')

from django.conf import settings
import os

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', null=True, blank=True)
    condition = models.CharField(max_length=255)  # Aggiungi questo campo


    def icon_url(self):
        if self.icon:
            return self.icon.url
        return settings.STATIC_URL + 'quiz_app/images/default_achievement.png'

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class QuizQuestion(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='questions')
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    question_number = models.IntegerField()
    user_answer = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, related_name='quiz_question_user_answers')
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('quiz_session', 'question_number')
        indexes = [
            models.Index(fields=['quiz_session', 'image']),
        ]

    def __str__(self):
        return f"Question {self.question_number} for {self.quiz_session}"

    def save(self, *args, **kwargs):
        if self.image:
            self.image = resize_image(self.image, 800, 600)
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)  # Nuovo campo


    class Meta:
        ordering = ['-created_at']



