import random
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db.models import Value
import logging
from .models import QuizQuestion, Observation
logger = logging.getLogger(__name__)


def get_weighted_random_species(region, month):
    from .models import Species, SpeciesAreaWeight, SpeciesPeriodWeight
    
    query = Species.objects.all()

    if region:
        query = query.filter(speciesareaweight__region=region, speciesareaweight__weight__gt=0)
    
    if month:
        query = query.filter(speciesperiodweight__month=month, speciesperiodweight__weight__gt=0)

    species_weights = query.annotate(
        final_weight=F('probability') * 
                     Coalesce(F('speciesareaweight__weight'), Value(1.0)) * 
                     Coalesce(F('speciesperiodweight__weight'), Value(1.0))
    ).values('id', 'name', 'final_weight')

    if not species_weights:
        return None, 0

    total_weight = sum(sw['final_weight'] for sw in species_weights)

    if total_weight == 0:
        return None, 0

    r = random.uniform(0, total_weight)
    upto = 0

    for sw in species_weights:
        if upto + sw['final_weight'] >= r:
            selected_species = Species.objects.get(id=sw['id'])
            return selected_species, sw['final_weight']
        upto += sw['final_weight']

    return None, 0

from django.db.models import Q
import random

from django.db.models import Q
from django.db import transaction
import random

from django.db.models import Q
from django.db import transaction
import random

def get_next_observation(user, species, quiz_session):
    with transaction.atomic():
        user_profile = user.userprofile
        history = user_profile.species_observation_history.get(str(species.id), [])
        
        all_observations = Observation.objects.filter(species=species)
        
        # Escludi le osservazioni già utilizzate in questo quiz
        used_observations = set(QuizQuestion.objects.filter(quiz_session=quiz_session).values_list('image__observation', flat=True))
        
        available_observations = all_observations.exclude(id__in=used_observations)
        
        if not available_observations:
            # Se non ci sono osservazioni disponibili, resetta la storia per questa specie
            available_observations = all_observations
            history = []
        
        # Escludi le ultime 15 osservazioni dalla storia dell'utente
        if history:
            available_observations = available_observations.exclude(id__in=history[-15:])
        
        if not available_observations:
            # Se ancora non ci sono osservazioni disponibili, usa tutte le osservazioni
            available_observations = all_observations
        
        if not available_observations:
            return None  # Non ci sono osservazioni per questa specie
        
        # Seleziona un'osservazione casuale tra quelle disponibili
        selected_observation = random.choice(list(available_observations))
        
        # Aggiorna la storia dell'utente
        history.append(selected_observation.id)
        user_profile.species_observation_history[str(species.id)] = history[-15:]  # Mantieni solo le ultime 15
        user_profile.save()
        
        return selected_observation