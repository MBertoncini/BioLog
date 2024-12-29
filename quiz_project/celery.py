import os
from celery import Celery

# Imposta la variabile d'ambiente di default per le impostazioni di Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_project.settings')

app = Celery('quiz_project')

# Usa una stringa qui per evitare che il worker non carichi l'oggetto al momento dell'avvio
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carica i task modules da tutte le app registrate in Django
app.autodiscover_tasks()