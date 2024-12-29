from django.urls import path
from . import views

app_name = 'unveiling'

urlpatterns = [
    path('', views.aesthetic_choice, name='aesthetic_choice'),
    path('results/', views.unveiling_results, name='results'),
]