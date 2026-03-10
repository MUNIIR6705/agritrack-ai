from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from animals.models import Animal, WeightRecord
from django.utils import timezone
from django.db.models import Q
import datetime

@login_required
def general_reports(request):
    """
    Dashboard summarizing farm performance.
    Calculates Total Farm Value (KES) based on current weight logs.
    """
    animals = Animal.objects.filter(owner=request.user, status='Active')
    market_price = 450
    total_value = 0
    
    for animal in animals:
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        if last_weight:
            total_value += float(last_weight.weight) * market_price

    return render(request, 'reports/general.html', {
        'total_farm_value': total_value,
        'animal_count': animals.count()
    })

@login_required
def market_readiness(request):
    """
    AI-driven Supply Chain Synchronization.
    Combines Growth Predictions (ADG) with Live Market Valuation (KES).
    """
    animals = Animal.objects.filter(owner=request.user, status='Active')
    predictions = [] 
    market_items = []
    target_weight = 90.0
    market_price_per_kg = 450 

    for animal in animals:
        # 1. Logic for Growth Predictions (Last 2 records)
        records = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded')[:2]
        
        if len(records) >= 2:
            latest, previous = records[0], records[1]
            weight_diff = float(latest.weight - previous.weight)
            days_diff = (latest.date_recorded - previous.date_recorded).days
            
            if days_diff > 0:
                adg = weight_diff / days_diff
                weight_left = target_weight - float(latest.weight)
                
                if adg <= 0:
                    status, pred_date, days_to_market = "Stagnant/Losing", "N/A", 0
                elif weight_left <= 0:
                    status, pred_date, days_to_market = "Ready for Market", timezone.now().date(), 0
                else:
                    days_to_market = weight_left / adg
                    pred_date = timezone.now().date() + datetime.timedelta(days=int(days_to_market))
                    status = "Growing"

                predictions.append({
                    'tag': animal.tag_number,
                    'species': animal.species,
                    'current_weight': latest.weight,
                    'adg': round(adg, 2),
                    'predicted_date': pred_date,
                    'days_left': int(days_to_market),
                    'status': status
                })
        else:
             predictions.append({
                    'tag': animal.tag_number,
                    'species': animal.species,
                    'current_weight': records[0].weight if records else 0,
                    'adg': 'N/A',
                    'predicted_date': 'Insufficient Data',
                    'status': 'Monitoring'
                })

        # 2. Logic for Live Marketplace Valuation (Latest record only)
        current_w = records[0].weight if records else 0
        market_items.append({
            'tag': animal.tag_number,
            'species': animal.species,
            'weight': current_w,
            'valuation': float(current_w) * market_price_per_kg,
            'status': 'Ready' if current_w >= target_weight else 'Growing'
        })

    # Sort predictions: Ready first
    predictions.sort(key=lambda x: (0 if x['status'] == "Ready for Market" else 1, 
                                   x['predicted_date'] if isinstance(x['predicted_date'], datetime.date) else datetime.date.max))

    return render(request, 'reports/market.html', {
        'predictions': predictions,
        'market_items': market_items,
        'target_weight': target_weight,
        'price_per_kg': market_price_per_kg,
        'market_date': timezone.now()
    })

@login_required
def market_view(request):
    """
    Standalone AgriMarket Marketplace View.
    Redirects or renders the same comprehensive market dashboard.
    """
    # Simply call market_readiness to keep data consistent across the Hub
    return market_readiness(request)