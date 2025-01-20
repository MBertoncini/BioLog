import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import random
from django.core.cache import cache
from .tasks import load_question
from django.template.loader import render_to_string
from django.urls import reverse
import logging
logger = logging.getLogger(__name__)
from django.views.decorators.http import require_POST
from .models import QuizSession, QuizQuestion, Species
from django.views.decorators.http import require_http_methods
from .tasks import load_question
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from .models import UserProfile, UserIncorrectAnswer, Species, UserAchievement
from .tasks import load_questions_async
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.db.models import Count, F, FloatField, Avg
from django.db.models.functions import TruncDate
import csv
from django.http import HttpResponse
from django.db.models import Count, F, Case, When, FloatField
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.templatetags.static import static
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .forms import UserProfileForm
import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F, FloatField, Avg, Case, When, Value, Q, CharField
from django.db.models.functions import TruncDate
from .models import Species, QuizSession, QuizQuestion
from django.http import HttpResponse
import csv
from .utils import get_weighted_random_species, get_next_observation
from django.db.models import CharField
from quiz_app.achievements import get_user_achievements
from django.contrib import messages


from .models import (
    Species, Region, Month, Observation, Image, QuizSession, 
    UserProfile, UserIncorrectAnswer, Achievement, UserAchievement, QuizQuestion, Image, Observation
)
from .inaturalist_api import get_inaturalist_images

def home(request):
    return render(request, 'quiz_app/home.html')

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F, FloatField, Avg, Case, When, Value, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from .models import Species, QuizSession, QuizQuestion, User
import csv

def can_view_statistics(user):
    return user.is_superuser or user.groups.filter(name='Statistics Viewers').exists()

@user_passes_test(can_view_statistics)
def statistics_view(request):
    family = request.GET.get('family')
    user_id = request.GET.get('user_id')
    
    context = {}

    # 1. Specie più difficili
    difficult_species = get_difficult_species(family, user_id)
    difficult_species_data = list(difficult_species.values('name', 'error_rate'))
    context['difficult_species'] = difficult_species_data
    print("Debug - Difficult Species:", difficult_species_data)

    # 2. Performance degli utenti
    user_performances = get_user_performances(family, user_id)
    avg_accuracy = user_performances.aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy']
    context['average_accuracy'] = avg_accuracy
    print("Debug - Average Accuracy:", avg_accuracy)

    # Distribuzione dei punteggi
    score_distribution = get_score_distribution(user_performances)
    score_distribution_data = list(score_distribution)
    context['score_distribution'] = score_distribution_data
    print("Debug - Score Distribution:", score_distribution_data)

    # Andamento nel tempo
    performance_trend = get_performance_trend(family, user_id)
    performance_trend_data = list(performance_trend)
    context['performance_trend'] = performance_trend_data
    print("Debug - Performance Trend:", performance_trend_data)

    # 3. Errori comuni
    common_errors = get_common_errors(family, user_id)
    common_errors_data = list(common_errors)
    context['common_errors'] = common_errors_data
    print("Debug - Common Errors:", common_errors_data)

    # Aggiungi le opzioni per i filtri
    context['families'] = Species.objects.values_list('family', flat=True).distinct()
    context['users'] = User.objects.all()

    return render(request, 'quiz_app/statistics.html', context)

def get_difficult_species(family=None, user_id=None):
    query = Species.objects.annotate(
        total_questions=Count('quizquestion'),
        incorrect_answers=Count('quizquestion', filter=Q(quizquestion__is_correct=False)),
        error_rate=Case(
            When(total_questions=0, then=0),
            default=F('incorrect_answers') * 100.0 / F('total_questions'),
            output_field=FloatField()
        )
    ).filter(total_questions__gt=10)

    if family:
        query = query.filter(family=family)
    if user_id:
        query = query.filter(quizquestion__quiz_session__user_id=user_id)

    return query.order_by('-error_rate')[:10]

def get_user_performances(family=None, user_id=None):
    query = QuizSession.objects.annotate(
        accuracy=Case(
            When(total_questions=0, then=0),
            default=F('score') * 100.0 / F('total_questions'),
            output_field=FloatField()
        )
    )

    if family:
        query = query.filter(quizquestion__species__family=family)
    if user_id:
        query = query.filter(user_id=user_id)

    return query

def get_score_distribution(user_performances):
    return user_performances.annotate(
        score_range=Case(
            When(accuracy__lt=20, then=Value('0-20%')),
            When(accuracy__lt=40, then=Value('21-40%')),
            When(accuracy__lt=60, then=Value('41-60%')),
            When(accuracy__lt=80, then=Value('61-80%')),
            default=Value('81-100%'),
            output_field=CharField()
        )
    ).values('score_range').annotate(count=Count('id'))

def get_performance_trend(family=None, user_id=None):
    query = QuizSession.objects.annotate(
        date=TruncDate('start_time'),
        accuracy=Case(
            When(total_questions=0, then=0),
            default=F('score') * 100.0 / F('total_questions'),
            output_field=FloatField()
        )
    )

    if family:
        query = query.filter(quizquestion__species__family=family)
    if user_id:
        query = query.filter(user_id=user_id)

    return query.values('date').annotate(avg_accuracy=Avg('accuracy')).order_by('date')

def get_common_errors(family=None, user_id=None):
    query = QuizQuestion.objects.filter(is_correct=False)

    if family:
        query = query.filter(species__family=family)
    if user_id:
        query = query.filter(quiz_session__user_id=user_id)

    return query.values('species__name', 'user_answer__name').annotate(count=Count('id')).order_by('-count')[:20]

def download_user_performance(request):
    family = request.GET.get('family')
    user_id = request.GET.get('user_id')
    
    user_performances = get_user_performances(family, user_id)
    score_distribution = get_score_distribution(user_performances)
    performance_trend = get_performance_trend(family, user_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_performance.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Distribuzione dei punteggi'])
    writer.writerow(['Range', 'Numero di quiz'])
    for dist in score_distribution:
        writer.writerow([dist['score_range'], dist['count']])
    
    writer.writerow([])
    writer.writerow(['Andamento nel tempo'])
    writer.writerow(['Data', 'Accuratezza media'])
    for trend in performance_trend:
        writer.writerow([trend['date'], f"{trend['avg_accuracy']:.2f}%"])
    
    return response

def download_common_errors(request):
    family = request.GET.get('family')
    user_id = request.GET.get('user_id')
    
    common_errors = get_common_errors(family, user_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="common_errors.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Specie corretta', 'Specie errata', 'Conteggio'])
    for error in common_errors:
        writer.writerow([error['species__name'], error['user_answer__name'], error['count']])
    
    return response

def download_all_statistics(request):
    family = request.GET.get('family')
    user_id = request.GET.get('user_id')
    
    difficult_species = get_difficult_species(family, user_id)
    user_performances = get_user_performances(family, user_id)
    score_distribution = get_score_distribution(user_performances)
    performance_trend = get_performance_trend(family, user_id)
    common_errors = get_common_errors(family, user_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_statistics.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['Specie più difficili'])
    writer.writerow(['Specie', 'Tasso di errore'])
    for species in difficult_species:
        writer.writerow([species.name, f"{species.error_rate:.2f}%"])
    
    writer.writerow([])
    writer.writerow(['Distribuzione dei punteggi'])
    writer.writerow(['Range', 'Numero di quiz'])
    for dist in score_distribution:
        writer.writerow([dist['score_range'], dist['count']])
    
    writer.writerow([])
    writer.writerow(['Andamento nel tempo'])
    writer.writerow(['Data', 'Accuratezza media'])
    for trend in performance_trend:
        writer.writerow([trend['date'], f"{trend['avg_accuracy']:.2f}%"])
    
    writer.writerow([])
    writer.writerow(['Errori comuni'])
    writer.writerow(['Specie corretta', 'Specie errata', 'Conteggio'])
    for error in common_errors:
        writer.writerow([error['species__name'], error['user_answer__name'], error['count']])
    
    return response

def debug_statistics(request):
    total_questions = QuizQuestion.objects.count()
    total_correct = QuizQuestion.objects.filter(is_correct=True).count()
    debug_info = f"Total questions: {total_questions}, Correct answers: {total_correct}\n\n"

    for species in Species.objects.all():
        questions = QuizQuestion.objects.filter(species=species)
        correct = questions.filter(is_correct=True).count()
        total = questions.count()
        if total > 0:
            error_rate = (1 - correct / total) * 100
            debug_info += f"{species.name}: {error_rate:.2f}% error rate ({correct}/{total})\n"

    return HttpResponse(debug_info, content_type="text/plain")

def download_difficult_species(request):
    family = request.GET.get('family')
    user_id = request.GET.get('user_id')
    
    difficult_species = get_difficult_species(family, user_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="difficult_species.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Specie', 'Tasso di errore'])
    for species in difficult_species:
        writer.writerow([species.name, f"{species.error_rate:.2f}%"])
    
    return response


def get_cached_questions():
    cached_questions = cache.get('preloaded_questions')
    if not cached_questions:
        cached_questions = preload_questions()
        cache.set('preloaded_questions', cached_questions, 3600)  # cache for 1 hour
    return cached_questions


@login_required
def start_quiz(request, quiz_type='text_input'):
    if request.method == 'POST':
        region_name = request.POST.get('region')
        month_name = request.POST.get('month')
        all_regions_months = request.POST.get('all_regions_months') == 'on'

        if all_regions_months or region_name == 'all':
            region = None
        else:
            region = get_object_or_404(Region, name=region_name)

        if all_regions_months or month_name == 'all':
            month = None
        else:
            month = get_object_or_404(Month, name=month_name)

        quiz_session = QuizSession.objects.create(
            user=request.user,
            region=region,
            month=month,
            quiz_type=quiz_type
        )
        load_questions_async.delay(quiz_session.id, 1, 10)
        return redirect('quiz_app:question', quiz_session_id=quiz_session.id, question_number=1)

    regions = Region.objects.all()
    months = Month.objects.all()
    return render(request, 'quiz_app/start_quiz.html', {'regions': regions, 'months': months, 'quiz_type': quiz_type})


from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import UserProfile
from django.db import transaction

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.db import transaction

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .models import UserProfile
from django.core.mail import EmailMessage

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .models import UserProfile
from django.core.mail import EmailMessage

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError

from django.contrib import messages
from django.db import IntegrityError

from django.contrib import messages
from django.db import IntegrityError

@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                profile = UserProfile.objects.get(user=user)
                
                current_site = get_current_site(request)
                subject = 'Attiva il tuo account Quiz Farfalle'
                html_message = render_to_string('email/confirmation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': profile.confirmation_token,
                })
                plain_message = strip_tags(html_message)
                from_email = 'noreply@quizfarfalle.com'
                to_email = user.email
                
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
                return render(request, 'registration/confirmation_sent.html')
            except IntegrityError as e:
                if 'unique constraint' in str(e).lower() and 'username' in str(e).lower():
                    messages.error(request, "Questo username è già in uso. Per favore, scegli un altro username.")
                elif 'unique constraint' in str(e).lower() and 'email' in str(e).lower():
                    messages.error(request, "Questa email è già registrata. Per favore, usa un'altra email o effettua il login.")
                else:
                    messages.error(request, "Si è verificato un errore durante la registrazione. Per favore, prova di nuovo.")
            except Exception as e:
                print(f"Failed to create user or send email: {str(e)}")
                messages.error(request, "Si è verificato un errore durante la registrazione. Per favore, prova di nuovo.")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# from django.utils.http import urlsafe_base64_decode
# from django.contrib.auth.models import User
# from django.utils.encoding import force_str

# def confirm_email(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and str(user.userprofile.confirmation_token) == str(token):
#         user.is_active = True
#         user.userprofile.email_confirmed = True
#         user.save()
#         user.userprofile.save()
#         login(request, user)
#         return redirect('quiz_app:home')
#     else:
#         return render(request, 'registration/confirmation_invalid.html')

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import login
from django.shortcuts import render, redirect

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and str(user.userprofile.confirmation_token) == str(token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('quiz_app:home')
    else:
        return render(request, 'registration/confirmation_invalid.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = redirect('home')  # o qualsiasi altra pagina dopo il login
            response['X-Just-Logged-In'] = 'true'
            return response
        else:
            messages.error(request, 'Username o password non validi.')
    return render(request, 'login.html')


def preload_questions(num_questions=10):
    questions = []
    for _ in range(num_questions):
        species = Species.objects.order_by('?').first()
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
            questions.append({
                'species': species,
                'image': image,
                'observation': observation
            })
    return questions



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from .models import QuizSession, QuizQuestion, Species, Image
from .utils import get_weighted_random_species, get_next_observation
from .quiz_logging import log_question_creation
from .tasks import load_question
import requests
import random
import logging
import time

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET", "POST"])
def question(request, quiz_session_id, question_number):
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    
    if question_number > 10:
        return redirect('quiz_app:quiz_results', quiz_session_id=quiz_session.id)

    if request.method == 'POST':
        return handle_post_request(request, quiz_session, question_number)
    
    return handle_get_request(request, quiz_session, question_number)

def handle_post_request(request, quiz_session, question_number):
    quiz_question = get_object_or_404(QuizQuestion, quiz_session=quiz_session, question_number=question_number)
    
    if quiz_session.quiz_type == 'multiple_choice':
        selected_species_id = request.POST.get('species')
        if selected_species_id:
            selected_species = get_object_or_404(Species, id=selected_species_id)
            quiz_question.user_answer = selected_species
            quiz_question.is_correct = (selected_species == quiz_question.species)
            if quiz_question.is_correct:
                quiz_session.score += 1
            quiz_question.save()
            quiz_session.save()
            
            next_question_number = question_number + 1
            if next_question_number <= 10:
                load_next_question(request, quiz_session.id, next_question_number)
            
            return redirect('quiz_app:question', quiz_session_id=quiz_session.id, question_number=next_question_number)
        else:
            messages.error(request, "Per favore, seleziona una risposta.")
    else:  # text_input
        user_answer = request.POST.get('species_name', '').strip().lower()
        correct_name = quiz_question.species.name.lower()
        correct_genus = correct_name.split()[0]
        
        valid_species = Species.objects.filter(name__iexact=user_answer).first()
        valid_genus = Species.objects.filter(name__istartswith=f"{user_answer} ").exists()
        
        if valid_species or valid_genus:
            if user_answer == correct_name:
                quiz_question.is_correct = True
                quiz_session.score += 1
            elif user_answer == correct_genus:
                quiz_question.is_correct = True
                quiz_session.score += 0.5
            else:
                quiz_question.is_correct = False
            
            quiz_question.user_answer = valid_species if valid_species else quiz_question.species
            quiz_question.save()
            quiz_session.save()
            
            next_question_number = question_number + 1
            if next_question_number <= 10:
                load_next_question(request, quiz_session.id, next_question_number)
            
            return redirect('quiz_app:question', quiz_session_id=quiz_session.id, question_number=next_question_number)
        else:
            messages.error(request, "La specie o il genere inserito non è valido. Per favore, riprova.")
    
    return handle_get_request(request, quiz_session, question_number)

def handle_get_request(request, quiz_session, question_number):
    quiz_question = QuizQuestion.objects.filter(quiz_session=quiz_session, question_number=question_number).first()
    if not quiz_question:
        quiz_question = create_new_question(request.user, quiz_session, question_number)
        if not quiz_question:
            return HttpResponse('Impossibile generare una domanda. Per favore, riprova più tardi.')
        
        if question_number < 10:
            load_next_question(request, quiz_session.id, question_number + 1)

    species_choices = list(Species.objects.exclude(id=quiz_question.species.id).order_by('?')[:3])
    species_choices.append(quiz_question.species)
    random.shuffle(species_choices)
    
    progress = (question_number / 10) * 100

    context = {
        'quiz_session': quiz_session,
        'image': quiz_question.image,
        'species_choices': species_choices,
        'question_number': question_number,
        'progress': progress,
    }
          
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'question_html': render_to_string('quiz_app/question_content.html', context, request=request),
            'progress': progress,
            'question_number': question_number
        })
    else:
        return render(request, 'quiz_app/question.html', context)

def create_new_question(user, quiz_session, question_number):
    quiz_question = QuizQuestion.objects.filter(
        quiz_session=quiz_session, 
        question_number=question_number
    ).first()
    
    if quiz_question:
        return quiz_question

    max_attempts = 20
    backoff_factor = 0.1
    for attempt in range(max_attempts):
        try:
            with transaction.atomic():
                filters = Q()
                if quiz_session.region and attempt < 10:
                    filters &= Q(speciesareaweight__region=quiz_session.region)
                if quiz_session.month and attempt < 15:
                    filters &= Q(speciesperiodweight__month=quiz_session.month)
                
                species = Species.objects.filter(filters).order_by('?').first()
                if not species:
                    continue
                
                observation = get_next_observation(user, species, quiz_session)
                if observation is None:
                    continue
                
                image = Image.objects.filter(observation=observation).first()
                if not image or not is_image_url_valid(image.url):
                    continue
                
                quiz_question = QuizQuestion.objects.create(
                    quiz_session=quiz_session,
                    question_number=question_number,
                    species=species,
                    image=image
                )
                log_question_creation(quiz_session.id, species.id, observation.id, image.id)
                return quiz_question
        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            time.sleep((2 ** attempt) * backoff_factor)
    
    logger.error(f"Failed to create question after {max_attempts} attempts")
    return None

def load_next_question(request, quiz_session_id, question_number):
    if question_number <= 10:
        load_question.delay(quiz_session_id, question_number)
    return JsonResponse({'status': 'ok'})

@login_required
def preload_next_question(request, quiz_session_id, question_number):
    if question_number <= 10:
        preload_next_question.delay(quiz_session_id, question_number)
    return JsonResponse({'status': 'ok'})

    
def is_image_url_valid(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

@login_required
@require_POST
def update_avatar(request):
    if 'avatar' in request.FILES:
        user_profile = request.user.userprofile
        
        # Se esiste già un avatar, eliminalo
        if user_profile.avatar:
            if os.path.isfile(user_profile.avatar.path):
                os.remove(user_profile.avatar.path)
        
        user_profile.avatar = request.FILES['avatar']
        user_profile.save()
        return JsonResponse({'success': True, 'avatar_url': user_profile.avatar.url})
    return JsonResponse({'success': False})

def calculate_statistics(profile_user):
    total_questions = QuizQuestion.objects.filter(quiz_session__user=profile_user).count()
    correct_answers = QuizQuestion.objects.filter(quiz_session__user=profile_user, is_correct=True).count()
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    return total_questions, correct_answers, accuracy

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, UserIncorrectAnswer, Species
from django.db.models import Count
from .achievements import get_user_achievements
from .forms import UserProfileForm, ChangeUsernameForm, ChangePasswordForm
from django.contrib.auth import update_session_auth_hash

@login_required
def user_profile(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    user_profile, created = UserProfile.objects.get_or_create(user=profile_user)

    if request.method == 'POST' and request.user == profile_user:
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profilo aggiornato con successo.')
        elif 'change_username' in request.POST:
            username_form = ChangeUsernameForm(request.POST, instance=profile_user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, 'Nome utente cambiato con successo.')
        elif 'change_password' in request.POST:
            password_form = ChangePasswordForm(profile_user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, profile_user)
                messages.success(request, 'Password cambiata con successo.')
        return redirect('quiz_app:user_profile', username=profile_user.username)

    form = UserProfileForm(instance=user_profile)
    username_form = ChangeUsernameForm(instance=profile_user)
    password_form = ChangePasswordForm(profile_user)

    total_questions = QuizQuestion.objects.filter(quiz_session__user=profile_user).count()
    correct_answers = QuizQuestion.objects.filter(quiz_session__user=profile_user, is_correct=True).count()
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    difficult_species = Species.objects.filter(quizquestion__quiz_session__user=profile_user, quizquestion__is_correct=False) \
        .annotate(incorrect_count=Count('quizquestion')) \
        .order_by('-incorrect_count')[:5]

    user_achievements = get_user_achievements(profile_user)
    earned_achievements = [achievement for achievement in user_achievements if achievement['is_earned']]

    is_own_profile = request.user == profile_user
    is_following = request.user.is_authenticated and not is_own_profile and request.user.userprofile.following.filter(user=profile_user).exists()

    context = {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'form': form,
        'username_form': username_form,
        'password_form': password_form,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy': accuracy,
        'difficult_species': difficult_species,
        'user_achievements': earned_achievements,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'followers': user_profile.followers.all(),
        'following': user_profile.following.all(),
    }

    return render(request, 'quiz_app/user_profile.html', context)

@login_required
def edit_profile(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        username_form = ChangeUsernameForm(request.POST, instance=request.user)
        password_form = ChangePasswordForm(request.user, request.POST)
        
        if form.is_valid() and username_form.is_valid():
            form.save()
            username_form.save()
            messages.success(request, 'Profilo aggiornato con successo.')
            
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password cambiata con successo.')
            
            return redirect('quiz_app:user_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=user_profile)
        username_form = ChangeUsernameForm(instance=request.user)
        password_form = ChangePasswordForm(request.user)

    context = {
        'form': form,
        'username_form': username_form,
        'password_form': password_form,
    }
    return render(request, 'quiz_app/edit_profile.html', context)

@login_required
def get_followers(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.userprofile.followers.all()
    followers_data = [{
        'username': follower.user.username,
        'avatar_url': follower.avatar.url if follower.avatar else static('quiz_app/images/default_avatar.png'),
        'is_following': request.user.userprofile.following.filter(user=follower.user).exists()
    } for follower in followers]
    return JsonResponse({'followers': followers_data})

@login_required
def get_following(request, username):
    user = get_object_or_404(User, username=username)
    following = user.userprofile.following.all()
    following_data = [{
        'username': followed.user.username,
        'avatar_url': followed.avatar.url if followed.avatar else static('quiz_app/images/default_avatar.png'),
        'is_following': request.user.userprofile.following.filter(user=followed.user).exists()
    } for followed in following]
    return JsonResponse({'following': following_data})


def user_search(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(username__icontains=query).select_related('userprofile')
    else:
        users = User.objects.none()
    return render(request, 'quiz_app/user_search.html', {'users': users, 'query': query})

from django.http import JsonResponse, HttpResponseBadRequest

@login_required
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    # Impedisci all'utente di seguire se stesso
    if request.user == user_to_follow:
        return HttpResponseBadRequest("Non puoi seguire te stesso.")
    
    user_profile = request.user.userprofile
    is_following = user_profile.following.filter(user=user_to_follow).exists()

    if is_following:
        user_profile.following.remove(user_to_follow.userprofile)
        is_following = False
    else:
        user_profile.following.add(user_to_follow.userprofile)
        is_following = True

    return JsonResponse({'is_following': is_following})

@login_required
def quiz_results(request, quiz_session_id):
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    quiz_session.end_time = timezone.now()
    quiz_session.save()
    # Aggiorna le statistiche dell'utente
    request.user.userprofile.update_stats()

    total_questions = quiz_session.total_questions
    correct_answers = quiz_session.score
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    difficult_species = get_difficult_species_for_user(request.user)
    performance_trend = get_performance_trend_for_user(request.user)

    achievements = check_achievements(request.user, accuracy)

    quiz_questions = QuizQuestion.objects.filter(quiz_session=quiz_session).order_by('question_number')

    context = {
        'quiz_session': quiz_session,
        'accuracy': accuracy,
        'difficult_species': difficult_species,
        'performance_trend': performance_trend,
        'achievements': achievements,
        'quiz_questions': quiz_questions,
    }

    return render(request, 'quiz_app/results.html', context)

def get_difficult_species_for_user(user):
    return QuizQuestion.objects.filter(quiz_session__user=user, is_correct=False) \
        .values('species__name') \
        .annotate(error_count=Count('id')) \
        .order_by('-error_count')[:5]

def get_performance_trend_for_user(user):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    return QuizSession.objects.filter(user=user, start_time__gte=thirty_days_ago) \
        .annotate(date=TruncDate('start_time'), accuracy=F('score') * 100.0 / F('total_questions')) \
        .values('date') \
        .annotate(avg_accuracy=Avg('accuracy')) \
        .order_by('date')

from .achievements import user_has_earned_quiz_master, user_has_earned_butterfly_expert, user_has_earned_sharp_eye, user_has_earned_legend

def check_achievements(user, accuracy):
    achievements = []
    
    achievement_conditions = [
        ("Quiz Master", user_has_earned_quiz_master(user)),
        ("Butterfly Expert", user_has_earned_butterfly_expert(user)),
        ("Sharp Eye", user_has_earned_sharp_eye(user)),
        ("Legend", user_has_earned_legend(user))
    ]

    for name, condition in achievement_conditions:
        if condition:
            achievement, _ = Achievement.objects.get_or_create(name=name)
            user_achievement, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created:
                achievements.append(achievement)

    return achievements

def all_achievements(request):
    all_achievements = Achievement.objects.all()
    user_achievements = get_user_achievements(request.user)
    
    achievements_data = []
    for achievement in all_achievements:
        user_achievement = next((ua for ua in user_achievements if ua['name'] == achievement.name), None)
        
        if user_achievement:
            progress = round(user_achievement['progress'])  # Arrotonda i decimali
            remaining = max(0, 100 - progress)
            
            encouragement = ""
            if achievement.name == "Sharp Eye" and progress < 100:
                encouragement = "Migliora l'accuratezza nei quiz! Devi ottenere almeno il 90%."
            
            achievements_data.append({
                'achievement': achievement,
                'is_earned': user_achievement['is_earned'],
                'date_earned': user_achievement['date_earned'] if user_achievement['is_earned'] else None,
                'progress': progress,
                'remaining': remaining,
                'encouragement': encouragement,
            })
        else:
            achievements_data.append({
                'achievement': achievement,
                'is_earned': False,
                'date_earned': None,
                'progress': 0,
                'remaining': 100,
                'encouragement': ""
            })
    
    return render(request, 'quiz_app/all_achievements.html', {'achievements_data': achievements_data})


@login_required
def random_users(request):
    try:
        all_users = list(User.objects.exclude(id=request.user.id).select_related('userprofile'))
        num_users = min(5, len(all_users))
        random_users = random.sample(all_users, num_users)
        
        users_data = []
        for user in random_users:
            try:
                avatar_url = user.userprofile.avatar.url if user.userprofile.avatar else static('quiz_app/images/default_avatar.png')
            except Exception as e:
                logger.error(f"Error getting avatar for user {user.username}: {str(e)}")
                avatar_url = static('quiz_app/images/default_avatar.png')
            
            is_following = request.user.userprofile.following.filter(user=user).exists()
            
            users_data.append({
                'username': user.username,
                'avatar_url': avatar_url,
                'is_following': is_following
            })
        
        return JsonResponse({'users': users_data})
    except Exception as e:
        logger.error(f"Error in random_users view: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'error': 'Si è verificato un errore interno.'}, status=500)

def performance_data(request, days):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    quiz_sessions = QuizSession.objects.filter(
        user=request.user,
        end_time__range=(start_date, end_date)
    ).order_by('end_time')
    
    labels = []
    accuracies = []
    
    for session in quiz_sessions:
        labels.append(session.end_time.strftime('%Y-%m-%d'))
        if session.total_questions > 0:  # Aggiungi questo controllo
            accuracy = (session.score / session.total_questions) * 100
        else:
            accuracy = 0  # O un altro valore predefinito
        accuracies.append(accuracy)
    
    return JsonResponse({
        'labels': labels,
        'accuracies': accuracies
    })

from django.contrib.auth.decorators import login_required
from .models import Notification

def notifications(request):
    notifications = request.user.notifications.all()
    return render(request, 'quiz_app/notifications.html', {'notifications': notifications})

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


from django.http import JsonResponse

def notification_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

from django.http import JsonResponse
# In views.py
from django.db import transaction

@transaction.atomic
def get_notifications(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.all().order_by('-created_at')[:5]
        print(f"Fetching notifications for user {request.user.username}: {notifications}")  # Aggiungi questa riga
        return JsonResponse({
            'notifications': [{
                'id': n.id,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M')
            } for n in notifications]
        })
    return JsonResponse({'notifications': []})

from django.http import JsonResponse
from .models import Species

from django.db.models import Q
from django.http import JsonResponse
from .models import Species

from django.http import JsonResponse
from .models import Species
import logging

logger = logging.getLogger(__name__)

def species_suggestions(request):
    print("species_suggestions view called")
    query = request.GET.get('query', '').capitalize()
    print(f"Query: {query}")
    logger.info(f"Received query: {query}")
    
    if not query:
        return JsonResponse({'suggestions': []})
    
    species_suggestions = list(Species.objects.filter(name__istartswith=query).values_list('name', flat=True)[:10])
    logger.info(f"Found suggestions: {species_suggestions}")
    
    # Aggiungi il genere se non è già presente nelle specie
    genus = query.split()[0]
    if genus not in species_suggestions:
        species_suggestions.insert(0, genus)
    
    return JsonResponse({'suggestions': species_suggestions})