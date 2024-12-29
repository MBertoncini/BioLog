from celery import shared_task
from django.db import transaction
from .models import QuizSession, QuizQuestion, Species, Image, Observation
from .inaturalist_api import get_inaturalist_images
import logging
from .models import UserProfile  # Aggiungi questa riga
from .utils import get_weighted_random_species

@shared_task
def load_question(quiz_session_id, question_number):
    quiz_session = QuizSession.objects.get(id=quiz_session_id)
    species, weight = get_weighted_random_species(quiz_session.region, quiz_session.month)
    
    inaturalist_data = get_inaturalist_images(species.name, max_results=1)
    if inaturalist_data:
        image_data = inaturalist_data[0]
        observation, _ = Observation.objects.get_or_create(
            inaturalist_id=image_data['inaturalist_id'],
            defaults={
                'species': species,
                'observed_on': image_data['observed_on'],
                'url': image_data['observation_url']
            }
        )
        image, _ = Image.objects.get_or_create(
            observation=observation,
            url=image_data['url'],
            defaults={
                'license_code': image_data['license_code'],
                'attribution': image_data['attribution']
            }
        )
        
        QuizQuestion.objects.create(
            quiz_session=quiz_session,
            species=species,
            image=image,
            question_number=question_number
        )
        return True
    return False

@shared_task
def load_questions_async(quiz_session_id, start_number, end_number):
    for question_number in range(start_number, end_number + 1):
        load_question.delay(quiz_session_id, question_number)

@shared_task
def clean_observation_history():
    for profile in UserProfile.objects.all():
        for species_id, history in profile.species_observation_history.items():
            # Mantieni solo le ultime 100 entry per specie, per esempio
            profile.species_observation_history[species_id] = history[-100:]
        profile.save()

@shared_task
def preload_next_question(quiz_session_id, question_number):
    if question_number <= 10:
        load_question(quiz_session_id, question_number)