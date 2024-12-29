from django.shortcuts import render, get_object_or_404
from .models import ButterflySpecies, Observation

def species_list(request):
    species = ButterflySpecies.objects.all()
    return render(request, 'butterfly_guide/species_list.html', {'species': species})

def species_detail(request, species_id):
    species = get_object_or_404(ButterflySpecies, id=species_id)
    return render(request, 'butterfly_guide/species_detail.html', {'species': species})

def search_species(request):
    # Implementa la logica di ricerca qui
    pass

def map_view(request):
    # Implementa la vista della mappa qui
    pass

def add_observation(request):
    # Implementa la logica per aggiungere un'osservazione
    pass