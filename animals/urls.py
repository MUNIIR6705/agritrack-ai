from django.urls import path
from . import views

# Namespacing is enabled. 
# Template tags must use 'animals:name' (e.g., {% url 'animals:add_animal' %})
app_name = 'animals'

urlpatterns = [
    # Main Roster / List View
    path('', views.animal_list, name='animal_list'),
    
    # Individual Animal Profile (e.g., /animals/5/)
    path('<int:animal_id>/', views.animal_detail, name='animal_detail'),
    
    # Form to register a new Pig or Rabbit
    path('add/', views.add_animal, name='add_animal'), 
]