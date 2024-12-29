from . import views
from django.contrib.auth import views as auth_views
from .models import QuizSession, UserAchievement, Achievement


def calculate_legend_progress(user):
    total_quizzes = QuizSession.objects.filter(user=user).count()
    total_required = 1000  # Numero totale per completare
    return min(total_quizzes / total_required * 100, 100)

def user_has_earned_legend(user):
    return QuizSession.objects.filter(user=user).count() >= 1000

def calculate_quiz_master_progress(user):
    total_required = 10  # Totale quiz da completare
    completed_quizzes = QuizSession.objects.filter(user=user).count()
    
    # Calcola la percentuale di completamento
    progress = (completed_quizzes / total_required) * 100
    
    # Assicurati che il progresso non superi il 100%
    return min(100, progress)


def user_has_earned_quiz_master(user):
    return QuizSession.objects.filter(user=user).count() >= 10

def calculate_butterfly_expert_progress(user):
    correct_answers = QuizSession.objects.filter(user=user, questions__is_correct=True).count()
    total_required = 100  # Richiesto rispondere correttamente a 100 domande
    return min(correct_answers / total_required * 100, 100)


def user_has_earned_butterfly_expert(user):
    unique_species = QuizSession.objects.filter(user=user).values('questions__species').distinct().count()
    return unique_species >= 100

def calculate_sharp_eye_progress(user):
    # Trova il quiz con la massima accuratezza dell'utente
    best_accuracy = QuizSession.objects.filter(user=user).order_by('-score').first()
    
    if best_accuracy:
        # Se l'accuratezza è >= 90%, l'obiettivo è raggiunto
        if best_accuracy.score >= 90:
            return 100  # Completato
        else:
            return 0  # Non ancora completato
    return 0  # Non ha fatto nessun quiz




def user_has_earned_sharp_eye(user):
    return QuizSession.objects.filter(user=user, score__gte=9).exists()

import logging
logger = logging.getLogger(__name__)

def get_user_achievements(user):
    achievements = []
    for achievement in Achievement.objects.all():
        progress_func = globals().get(f"calculate_{achievement.condition}_progress")
        earned_func = globals().get(f"user_has_earned_{achievement.condition}")
        
        if progress_func and earned_func:
            logger.debug(f"Calculating achievement: {achievement.name}")
            is_earned = earned_func(user)
            progress = progress_func(user)
            logger.debug(f"Achievement {achievement.name}: Earned: {is_earned}, Progress: {progress}")
            
            user_achievement = UserAchievement.objects.filter(user=user, achievement=achievement).first()
            
            achievements.append({
                'name': achievement.name,
                'description': achievement.description,
                'progress': progress,
                'encouragement': "Continua così, sei sulla buona strada!",
                'is_earned': is_earned,
                'date_earned': user_achievement.date_earned if user_achievement else None,
                'icon_url': achievement.icon_url()
            })
    
    return achievements