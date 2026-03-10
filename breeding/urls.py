from django.urls import path
from . import views

# Namespacing is enabled. 
# All reverse lookups now require the 'breeding:' prefix.
# Example: {% url 'breeding:breeding_list' %} or redirect('breeding:breeding_list')
app_name = 'breeding'

urlpatterns = [
    # 1. Main Breeding Dashboard / Birth Calendar
    # URL: /breeding/list/
    path('list/', views.breeding_list, name='breeding_list'),
    
    # 2. Form to record a mating event and trigger AI predictions
    # URL: /breeding/add/
    path('add/', views.add_breeding, name='add_breeding'),
    
    # 3. AJAX endpoint used by the 'Run AI Prediction' button in the form
    # This must match your JavaScript fetch() call exactly.
    # URL: /breeding/ajax/predict-gestation/
    path('ajax/predict-gestation/', views.predict_gestation_api, name='predict_gestation_api'),
    
    # 4. Action endpoint to record a successful birth
    # Transitions record status from 'Pregnant' to 'Delivered'
    # URL: /breeding/mark-delivered/5/
    path('mark-delivered/<int:record_id>/', views.mark_delivered, name='mark_delivered'),
]