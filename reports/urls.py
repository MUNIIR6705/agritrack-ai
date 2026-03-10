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
    
    # 3. The AgriMarket Hub
    # This matches the 'Open AgriMarket' button link: {% url 'reports:market_list' %}
    # URL: /reports/market/
    path('market/', views.market_view, name='market_list'),
]