from django.urls import path
from . import views

app_name = 'butterfly_guide'

urlpatterns = [
    path('', views.species_list, name='species_list'),
    path('species/<int:species_id>/', views.species_detail, name='species_detail'),
    path('search/', views.search_species, name='search_species'),
    path('map/', views.map_view, name='map_view'),
    path('add_observation/', views.add_observation, name='add_observation'),
]