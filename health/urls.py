from django.urls import path
from . import views

# Namespacing: All templates must use 'health:view_name'
app_name = 'health'

urlpatterns = [
    # 1. Main Dashboard - The Hub for Health Alerts & Financials
    path('dashboard/', views.health_dashboard, name='health_dashboard'),
    
    # 2. AI Veterinary Surveillance (Diagnostic Risk Engine)
    path('add/', views.add_health_record, name='add_health_record'),
    path('suggest-treatment/', views.suggest_treatment, name='suggest_treatment'),
    
    # 3. Growth & Performance Tracking (ADG Monitoring)
    path('weight/', views.record_weight, name='record_weight'),
    
    # 4. Breeding & ML Gestation Logic (Predictive Breeding)
    path('predict-gestation/', views.predict_gestation_api, name='predict_gestation_api'),

    # 5. Financial Management (M-Pesa Daraja 3.0 Integration)
    path('financials/', views.financial_reports, name='financial_reports'),
    path('financials/add/', views.add_transaction, name='add_transaction'),
    
    # PROPOSAL FEATURE: Automated Payment Confirmation
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # 6. Farmer Profile 
    path('profile/', views.profile_page, name='profile_page'),

    # --- NEW: SUPPLY CHAIN & REVENUE MODULES ---

    # 7. PROPOSAL FEATURE: Supply Chain Synchronization (Market Hub)
    # URL: /health/market-hub/
    # Logic: Only shows "AI Verified Healthy" stock that meets weight requirements.
    path('market-hub/', views.market_hub, name='market_hub'),

    # 8. PROPOSAL FEATURE: Digital Identification Framework (UEP Passport)
    # URL: /health/passport/<id>/
    # Displays the animal's cryptographically unique digital history for buyers.
    path('passport/<int:animal_id>/', views.animal_digital_passport, name='animal_digital_passport'),

    # 9. PROPOSAL FEATURE: Subscription-Based Revenue Model
    # URL: /health/upgrade/
    # Handles SaaS billing for premium AI features (Risk Engine & Predictive Breeding).
    path('upgrade/', views.upgrade_subscription, name='upgrade_subscription'),
]