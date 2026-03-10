from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard
    path('dashboard/', views.farmer_dashboard, name='dashboard'),
    
    # AJAX Endpoint for Weather Refresh
    path('ajax/refresh-weather/', views.refresh_weather_api, name='refresh_weather_api'),
]