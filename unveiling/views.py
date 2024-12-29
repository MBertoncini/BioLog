import os
import random
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from quiz_app.models import Species
from .models import AestheticChoice
from django.db import IntegrityError
from django.db.models import Count

logger = logging.getLogger(__name__)

@login_required
def aesthetic_choice(request):
    logger.info("Entering aesthetic_choice view")
    
    if request.method == 'POST':
        logger.info("POST request received")
        chosen_image = request.POST.get('chosen_image')
        species_name = chosen_image.split('.')[0].replace('_', ' ').title()
        species = Species.objects.filter(name__iexact=species_name).first()
        
        if species:
            try:
                AestheticChoice.objects.create(
                    user=request.user,
                    species=species,
                    image_filename=chosen_image
                )
            except IntegrityError:
                logger.warning(f"Duplicate choice for user {request.user.username}, species {species.name}, image {chosen_image}")
        else:
            logger.error(f"Species not found for image: {chosen_image}")
        
        # Remove shown images from the session
        shown_images = request.session.get('shown_images', [])
        if chosen_image in shown_images:
            shown_images.remove(chosen_image)
        request.session['shown_images'] = shown_images
        
        return redirect('unveiling:aesthetic_choice')

    image_dir = os.path.join(settings.MEDIA_ROOT, 'butterfly_images')
    all_images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    # Get the list of images already shown to the user
    shown_images = request.session.get('shown_images', [])
    
    # If all images have been shown, reset the list
    if len(shown_images) >= len(all_images) - 1:
        shown_images = []
    
    # Select images that haven't been shown yet
    available_images = [img for img in all_images if img not in shown_images]
    
    if len(available_images) < 2:
        logger.error("Not enough images available")
        return render(request, 'unveiling/error.html', {'message': 'Not enough images available'})
    
    chosen_images = random.sample(available_images, 2)
    
    # Add chosen images to the shown images list
    shown_images.extend(chosen_images)
    request.session['shown_images'] = shown_images
    
    images = []
    for image in chosen_images:
        images.append({
            'image_url': f'{settings.MEDIA_URL}butterfly_images/{image}',
            'filename': image
        })

    return render(request, 'unveiling/aesthetic_choice.html', {'images': images})

@login_required
def unveiling_results(request):
    top_species = AestheticChoice.objects.values('species__name') \
                                         .annotate(count=Count('species')) \
                                         .order_by('-count')[:10]
    
    labels = [species['species__name'] for species in top_species]
    data = [species['count'] for species in top_species]
    
    context = {
        'labels': labels,
        'data': data,
    }
    
    return render(request, 'unveiling/results.html', context)