from django.urls import path
from . import views

# Namespacing: All templates must use 'health:view_name'
app_name = 'health'

urlpatterns = [
    # 0. SECURITY CORE: Identity Verification (2FA)
    # URL: /health/verify-2fa/
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),

    # 1. MAIN DASHBOARD: Precision Node Hub
    path('dashboard/', views.health_dashboard, name='health_dashboard'),
    
    # 2. AI VETERINARY SURVEILLANCE: (Diagnostic Risk Engine)
    path('add/', views.add_health_record, name='add_health_record'),
    path('suggest-treatment/', views.suggest_treatment, name='suggest_treatment'),
    
    # 3. GROWTH & PERFORMANCE TRACKING: (Weight Registry)
    path('weight/', views.record_weight, name='record_weight'),
    
    # 4. BREEDING & ML GESTATION LOGIC: (Predictive Breeding)
    path('predict-gestation/', views.predict_gestation_api, name='predict_gestation_api'),

    # 5. FINANCIAL MANAGEMENT: (M-Pesa Daraja 3.0 Integration)
    path('financials/', views.financial_reports, name='financial_reports'),
    path('financials/add/', views.add_transaction, name='add_transaction'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # 6. FARMER IDENTITY NODE: (Metadata Synchronization)
    path('profile/', views.profile_page, name='profile_page'),

    # --- SUPPLY CHAIN & ECONOMIC VELOCITY MODULES ---

    # 7. MARKET VALUATION: (Economic Yield Analysis)
    # Calculates real-time worth based on March 2026 Kenyan Spot Prices
    path('valuation/', views.market_valuation, name='market_valuation'),

    # 7.5 M-PESA STK PUSH: (Digital Checkout Node)
    # Triggers the Safaricom Daraja API to prompt the buyer's phone
    path('initiate-sale/<int:animal_id>/', views.initiate_sale, name='initiate_sale'),

    # 8. SUPPLY CHAIN SYNC: (Market Hub)
    # Filters "Market Ready" stock for procurement managers
    path('market-hub/', views.market_hub, name='market_hub'),

    # 9. DIGITAL IDENTIFICATION: (UEP Passport)
    # Unique digital history for traceability and buyers
    path('passport/<int:animal_id>/', views.animal_digital_passport, name='animal_digital_passport'),

    # 10. SAAS REVENUE MODEL: (Premium AI Activation)
    path('upgrade/', views.upgrade_subscription, name='upgrade_subscription'),
    path('receipt/<int:animal_id>/', views.diagnostic_receipt, name='diagnostic_receipt'),
]