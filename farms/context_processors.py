import datetime
from animals.models import Animal, WeightRecord
from health.models import HealthRecord
from .weather_service import get_dynamic_weather 

def notifications(request):
    """
    Global context processor for AgriTrack.
    Handles Health Alerts, Resource Inventory, Financial Analytics, 
    and Hyper-local Weather for Kutus and beyond.
    """
    if request.user.is_authenticated:
        # 1. Health & Critical Alerts
        sick_animals_list = Animal.objects.filter(
            owner=request.user, 
            status__in=['Sick', 'Quarantined']
        ).select_related('owner')

        health_alerts_count = sick_animals_list.count()
        critical_cases_count = HealthRecord.objects.filter(
            animal__owner=request.user,
            severity__in=['High', 'Critical']
        ).count()

        # 2. Optimized Weather & Location Logic
        # This calls the service that defaults to Kutus to prevent UI hangs
        weather_data = get_dynamic_weather()
        live_temp = weather_data.get('temp', 22)
        location = weather_data.get('location', 'Kutus, KE')

        # 3. AI Risk Sentinel (Cold/Heat Stress)
        current_hour = datetime.datetime.now().hour
        is_cold_period = current_hour < 7 or current_hour > 19
        
        if live_temp >= 28:
            ai_risk_level = "High"
            ai_risk_msg = f"Heat Stress in {location}! Ensure ventilation and cool water."
        elif is_cold_period or live_temp < 15:
            ai_risk_level = "High"
            ai_risk_msg = f"Cold Stress in {location}. Keep bedding dry to prevent infections."
        else:
            ai_risk_level = "Low"
            ai_risk_msg = f"Ideal conditions in {location} for livestock growth."

        # 4. Resource Monitor (Feed Stock Velocity)
        active_animals = Animal.objects.filter(owner=request.user, status='Active')
        total_active_count = active_animals.count()
        
        bags_on_hand = 5 
        avg_consumption_rate = 0.15 
        
        if total_active_count > 0:
            daily_burn = total_active_count * avg_consumption_rate
            feed_days_left = int(bags_on_hand / daily_burn)
        else:
            feed_days_left = 30
            
        feed_status = "Optimal"
        if feed_days_left < 3:
            feed_status = "Critical"
        elif feed_days_left < 7:
            feed_status = "Low"

        # 5. Financial Intelligence (ROI & Asset Valuation)
        market_price = 450
        total_valuation = 0
        
        for animal in active_animals:
            last_w = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
            weight = float(last_w.weight) if last_w else 0
            total_valuation += weight * market_price
            
        total_investment = 15000 
        roi_percentage = 0
        if total_investment > 0:
            roi_percentage = round(((total_valuation - total_investment) / total_investment) * 100, 1)

        return {
            'notification_count': health_alerts_count + critical_cases_count,
            'sidebar_alerts': health_alerts_count,
            'critical_total': critical_cases_count,
            'sick_animals_list': sick_animals_list,
            'ai_risk_level': ai_risk_level,
            'ai_risk_msg': ai_risk_msg,
            'weather': weather_data,
            'feed_days_left': feed_days_left,
            'feed_status': feed_status,
            'feed_percentage': min(100, (feed_days_left / 14) * 100),
            'total_farm_value': total_valuation,
            'farm_roi': roi_percentage,
            'financial_status': "Profitable" if roi_percentage > 0 else "Startup/Growth",
        }
        
    return {
        'notification_count': 0,
        'sidebar_alerts': 0,
        'critical_total': 0,
        'sick_animals_list': [],
        'ai_risk_level': 'Low',
        'ai_risk_msg': 'Log in for analysis.',
        'weather': {'temp': '22', 'location': 'Kutus, KE', 'icon': 'cloud-sun'},
        'feed_days_left': 0,
        'feed_status': 'N/A',
        'feed_percentage': 0,
        'total_farm_value': 0,
        'farm_roi': 0,
        'financial_status': 'N/A',
    }