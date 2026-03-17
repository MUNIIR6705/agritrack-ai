from django.urls import path
from . import views

# Namespacing is critical. Templates must use {% url 'reports:name' %}
app_name = 'reports'

urlpatterns = [
    # 1. General Reports Dashboard
    # URL: /reports/
    path('', views.general_reports, name='general_reports'),
    
    # 2. AI Market Readiness Predictor
    # This is the "Brain" that calculates ADG and growth trajectories
    # URL: /reports/readiness/
    path('readiness/', views.market_readiness, name='market_readiness'),
    
    # 3. The AgriMarket Hub (Marketplace Listings)
    # URL: /reports/market/
    path('market/', views.market_view, name='market_list'),

    # 4. Marketplace Hub (The New Targeted Destination)
    # This matches the button link: {% url 'reports:marketplace_hub' %}
    # URL: /reports/marketplace-hub/
    path('marketplace-hub/', views.marketplace_hub_view, name='marketplace_hub'),
]