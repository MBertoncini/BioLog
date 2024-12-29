from django.contrib.auth.models import User
from django.db.models import Count, Sum, F
from quiz_app.models import QuizSession, QuizQuestion, UserIncorrectAnswer

# Sostituisci con l'ID dell'utente desiderato
user_id = 1

# Ottieni l'utente
user = User.objects.get(id=user_id)

# Conta i quiz completati
quiz_completati = QuizSession.objects.filter(user=user, end_time__isnull=False).count()

# Conta le risposte totali, corrette e sbagliate
statistiche_quiz = QuizQuestion.objects.filter(quiz_session__user=user).aggregate(
    totale_risposte=Count('id'),
    risposte_corrette=Sum('is_correct'),
)

# Calcola le risposte sbagliate
risposte_sbagliate = statistiche_quiz['totale_risposte'] - statistiche_quiz['risposte_corrette']

# Stampa i risultati
print(f"Statistiche per l'utente {user.username}:")
print(f"Quiz completati: {quiz_completati}")
print(f"Risposte totali: {statistiche_quiz['totale_risposte']}")
print(f"Risposte corrette: {statistiche_quiz['risposte_corrette']}")
print(f"Risposte sbagliate: {risposte_sbagliate}")

# Calcola la percentuale di accuratezza
if statistiche_quiz['totale_risposte'] > 0:
    accuratezza = (statistiche_quiz['risposte_corrette'] / statistiche_quiz['totale_risposte']) * 100
    print(f"Accuratezza: {accuratezza:.2f}%")
else:
    print("Nessuna risposta registrata.")

# Bonus: Ottieni le specie più difficili per questo utente
specie_difficili = UserIncorrectAnswer.objects.filter(user=user) \
    .values('species__name') \
    .annotate(count=Count('id')) \
    .order_by('-count')[:5]

print("\nLe 5 specie più difficili per questo utente:")
for specie in specie_difficili:
    print(f"- {specie['species__name']}: {specie['count']} errori")