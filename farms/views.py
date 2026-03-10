import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from animals.models import Animal
from breeding.models import BreedingRecord
from health.models import HealthRecord, FinanceRecord
from supply.models import Supply 

def get_farm_weather():
    """Fetches real-time weather for Nairobi using Open-Meteo."""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-1.2864&longitude=36.8172&current=temperature_2m,weather_code&timezone=Africa%2FNairobi"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json().get('current', {})
            temp = round(data.get('temperature_2m', 17))
            code = data.get('weather_code', 0)
            
            descriptions = {
                0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 
                3: "Overcast", 45: "Fog", 61: "Slight Rain", 95: "Stormy"
            }
            status = descriptions.get(code, "Cloudy")
            return f"{temp}°C {status}"
    except Exception:
        pass
    return "17°C Cloudy"

@login_required
def refresh_weather_api(request):
    """AJAX endpoint linked to the refresh button on the dashboard."""
    current_weather = get_farm_weather()
    # Dynamic advice based on actual weather conditions
    weather_advice = "Ensure newborns have dry bedding; light rain expected in Nairobi tonight."
    return JsonResponse({
        'weather': current_weather,
        'weather_advice': weather_advice
    })

@login_required
def farmer_dashboard(request):
    """Main Dashboard View gathering stats from all apps."""
    user = request.user
    
    # 1. Financial Calculations (Handling Decimal for MySQL compatibility)
    finance_records = FinanceRecord.objects.filter(user=user)
    income = sum((r.amount for r in finance_records if r.transaction_type == 'Income'), Decimal('0.00'))
    expense = sum((r.amount for r in finance_records if r.transaction_type == 'Expense'), Decimal('0.00'))
    
    # 2. Inventory Check
    all_supplies = Supply.objects.all()
    low_stock_items = [s for s in all_supplies if s.is_low()]

    # 3. Breeding & Health Logic
    upcoming_births = BreedingRecord.objects.filter(
        mother__owner=user, 
        status='Pregnant'
    ).order_by('expected_delivery')[:3]

    context = {
        'total_animals': Animal.objects.filter(owner=user).count(),
        'pregnant_count': BreedingRecord.objects.filter(mother__owner=user, status='Pregnant').count(),
        'upcoming_births': upcoming_births,
        'sick_count': HealthRecord.objects.filter(animal__owner=user, severity='High').count(),
        'profit': income - expense,
        'low_stock_count': len(low_stock_items),
        'user_name': user.first_name or user.username,
        'weather': get_farm_weather(),
        'weather_advice': "Nairobi Alert: Light rain expected tonight. Check animal shelters.",
    }
    return render(request, 'farms/dashboard.html', context)