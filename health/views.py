import json
import base64
import requests
import re
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.conf import settings

# 2026 MODERN SDK
from google import genai

# Import models & ML Engine
from animals.models import Animal, WeightRecord
from breeding.models import BreedingRecord 
from breeding.ai_models import BreedingPredictor 
from .models import HealthRecord, FinanceRecord

# --- EXTERNAL AI CONFIG ---
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# --- M-PESA DARAJA API CONFIG ---
MPESA_SHORTCODE = getattr(settings, 'MPESA_SHORTCODE', '174379')
MPESA_PASSKEY = getattr(settings, 'MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')

def get_mpesa_token():
    """Helper: Fetches OAuth2 token from Safaricom Daraja 3.0"""
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        r = requests.get(
            api_url, 
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), 
            timeout=5
        )
        return r.json().get('access_token')
    except Exception as e:
        print(f"M-Pesa Token Error: {e}")
        return None

# --- REVENUE MODEL: SUBSCRIPTION GATEKEEPER ---

def is_premium_user(user):
    """
    PROPOSAL FEATURE: SaaS Monetization.
    Checks if user has a confirmed 'Subscription' record in the last 30 days.
    """
    return FinanceRecord.objects.filter(
        user=user,
        category='Subscription',
        is_confirmed=True,
        date__gte=timezone.now() - timedelta(days=30)
    ).exists()

# --- M-PESA CALLBACK VIEW ---
@csrf_exempt
def mpesa_callback(request):
    """Notification from Safaricom to update transaction status automatically."""
    if request.method == "POST":
        try:
            stk_data = json.loads(request.body)
            result_code = stk_data['Body']['stkCallback']['ResultCode']
            checkout_id = stk_data['Body']['stkCallback']['CheckoutRequestID']

            if result_code == 0:
                FinanceRecord.objects.filter(checkout_request_id=checkout_id).update(
                    is_confirmed=True,
                    description="M-Pesa Payment Confirmed"
                )
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except Exception:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error"})

# --- DASHBOARD & HEALTH VIEWS ---

@login_required
def health_dashboard(request):
    """Intelligent Dashboard: Fulfills 'Early Detection' and 'Breeding Prediction' objectives."""
    all_animals = Animal.objects.filter(owner=request.user)
    active_animals = all_animals.filter(status='Active')
    
    critical_alerts = HealthRecord.objects.filter(
        animal__owner=request.user, 
        severity='High',
        date_recorded__gte=timezone.now() - timedelta(days=3)
    ).order_by('-date_recorded')

    upcoming_births = BreedingRecord.objects.filter(
        mother__owner=request.user,
        status='Confirmed',
        expected_delivery__lte=timezone.now().date() + timedelta(days=14),
        expected_delivery__gte=timezone.now().date()
    ).order_by('expected_delivery')

    finance = FinanceRecord.objects.filter(user=request.user)
    income = finance.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = finance.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

    market_price = 450
    total_farm_value = 0
    for animal in active_animals:
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        if last_weight:
            total_farm_value += float(last_weight.weight) * market_price

    context = {
        'user_name': request.user.username.title(),
        'total_livestock': active_animals.count(),
        'health_alerts': critical_alerts.count(),
        'critical_cases': critical_alerts,
        'upcoming_births': upcoming_births if is_premium_user(request.user) else [],
        'profit': income - expense,
        'total_farm_value': total_farm_value,
        'is_premium': is_premium_user(request.user),
        'recent_searches': HealthRecord.objects.filter(animal__owner=request.user).order_by('-date_recorded')[:5],
    }
    return render(request, 'health/dashboard.html', context)

@csrf_exempt
@login_required
def suggest_treatment(request):
    """PROPOSAL FEATURE: Diagnostic Risk Engine (Classification-based)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            symptoms = data.get('symptoms', '').lower()
            species = data.get('species', 'livestock').lower()
            
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                config={
                    'system_instruction': (
                        f"You are the AgriTrack AI Diagnostic Engine for {species}. "
                        "Return ONLY a JSON object with: diagnosis, severity (Low, Medium, High), "
                        "treatment (exact pharmacological names), and risk_factor (1-10)."
                    ),
                },
                contents=f"Symptoms: {symptoms}.",
            )
            
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                ai_data = json.loads(match.group())
                return JsonResponse({
                    "status": "success", 
                    "diagnosis": ai_data.get('diagnosis'), 
                    "treatment": ai_data.get('treatment'), 
                    "severity": ai_data.get('severity'),
                    "is_critical": ai_data.get('risk_factor', 0) >= 8
                })
            raise ValueError("Invalid AI Output")
        except Exception:
            return JsonResponse({"status": "success", "diagnosis": "System Safe-Mode", "treatment": "Broad-spectrum Rx", "severity": "Medium"})
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=400)

# --- NEW: SUPPLY CHAIN & REVENUE VIEWS ---

@login_required
def animal_digital_passport(request, animal_id):
    """PROPOSAL FEATURE: Digital Identification Framework (UEP History)."""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    health_history = HealthRecord.objects.filter(animal=animal).order_by('-date_recorded')
    weight_history = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded')
    
    return render(request, 'health/animal_passport.html', {
        'animal': animal,
        'health_history': health_history,
        'weight_history': weight_history,
    })

@login_required
def market_hub(request):
    """PROPOSAL FEATURE: Supply Chain Synchronization. Restricted to Premium."""
    if not is_premium_user(request.user):
        messages.warning(request, "The Market Hub is a Premium AI feature. Please upgrade to access.")
        return redirect('health:upgrade_subscription')

    active_animals = Animal.objects.filter(owner=request.user, status='Active')
    market_ready_stock = []

    for animal in active_animals:
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        is_healthy = not HealthRecord.objects.filter(
            animal=animal, severity='High', 
            date_recorded__gte=timezone.now() - timedelta(days=30)
        ).exists()

        if last_weight and is_healthy:
            ready = (animal.species == 'Pig' and last_weight.weight >= 60) or \
                    (animal.species == 'Rabbit' and last_weight.weight >= 2.5)
            if ready:
                market_ready_stock.append({
                    'animal': animal, 'weight': last_weight.weight, 'uep': animal.uep_code
                })

    return render(request, 'health/market_hub.html', {'ready_stock': market_ready_stock})

@login_required
def upgrade_subscription(request):
    """PROPOSAL FEATURE: SaaS Revenue Model. Triggers M-Pesa upgrade."""
    if request.method == "POST":
        messages.info(request, "Redirecting to M-Pesa for Premium AI activation (KES 1,000)...")
        # Pre-fills the transaction form for the user
        return render(request, 'health/add_transaction.html', {
            'category': 'Subscription',
            'amount': 1000,
            'description': 'AgriTrack AI Pro Monthly Subscription'
        })
    return render(request, 'health/upgrade.html')

# --- CORE UTILITY VIEWS ---

@login_required
def add_transaction(request):
    """Handles Cash and M-Pesa automated billing."""
    if request.method == "POST":
        t_type = request.POST.get('type', 'Expense')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        payment_method = request.POST.get('payment_method')
        mpesa_number = request.POST.get('mpesa_number')

        try:
            if payment_method == 'M-Pesa':
                access_token = get_mpesa_token()
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password_str = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
                password = base64.b64encode(password_str.encode()).decode('utf-8')
                phone = f"254{mpesa_number[-9:]}"
                
                payload = {
                    "BusinessShortCode": MPESA_SHORTCODE, "Password": password, 
                    "Timestamp": timestamp, "TransactionType": "CustomerPayBillOnline", 
                    "Amount": int(float(amount)), "PartyA": phone, 
                    "PartyB": MPESA_SHORTCODE, "PhoneNumber": phone,
                    "CallBackURL": "https://your-ngrok-url.app/health/mpesa-callback/", 
                    "AccountReference": "AgriTrackAI", "TransactionDesc": description
                }
                
                r = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", 
                                  json=payload, headers={"Authorization": f"Bearer {access_token}"})
                
                res_data = r.json()
                if res_data.get('ResponseCode') == '0':
                    checkout_id = res_data.get('CheckoutRequestID')
                    FinanceRecord.objects.create(
                        user=request.user, transaction_type=t_type, category=category, amount=amount, 
                        checkout_request_id=checkout_id,
                        description=f"{description} (Ref: {checkout_id} - M-Pesa Pending)"
                    )
                    messages.success(request, "M-Pesa STK Push Sent. Confirm on your phone.")
                else:
                    messages.error(request, f"M-Pesa failed: {res_data.get('CustomerMessage')}")
            else:
                FinanceRecord.objects.create(user=request.user, transaction_type=t_type, category=category, amount=amount, description=description, is_confirmed=True)
                messages.success(request, "Transaction recorded.")
            
            return redirect('health:financial_reports')
        except Exception as e:
            messages.error(request, f"Finance Error: {str(e)}")
            
    return render(request, 'health/add_transaction.html')

@login_required
def financial_reports(request):
    records = FinanceRecord.objects.filter(user=request.user).order_by('-date')
    income = records.filter(transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = records.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'health/financial_reports.html', {'records': records, 'income': income, 'expense': expense, 'profit': income - expense})

@login_required
def add_health_record(request):
    if request.method == "POST":
        animal_id = request.POST.get('animal')
        symptoms = request.POST.get('symptoms')
        severity = request.POST.get('severity')
        diagnosis = request.POST.get('diagnosis', '')
        treatment = request.POST.get('treatment', '')
        try:
            animal = Animal.objects.get(id=animal_id, owner=request.user)
            HealthRecord.objects.create(animal=animal, symptoms=symptoms, severity=severity, diagnosis=diagnosis, treatment=treatment)
            messages.success(request, "Health record saved.")
            return redirect('health:health_dashboard')
        except Exception:
            messages.error(request, "Error saving record.")
    animals = Animal.objects.filter(owner=request.user, status='Active')
    return render(request, 'health/add_health_record.html', {'animals': animals})

@login_required
def record_weight(request):
    preselected_id = request.GET.get('animal')
    if request.method == "POST":
        animal_id = request.POST.get('animal')
        weight = request.POST.get('weight')
        animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
        WeightRecord.objects.create(animal=animal, weight=weight)
        messages.success(request, "Weight log saved.")
        return redirect('health:health_dashboard')
    animals = Animal.objects.filter(owner=request.user, status='Active')
    return render(request, 'health/record_weight.html', {'animals': animals, 'preselected_id': preselected_id})

@login_required
def predict_gestation_api(request):
    animal_id = request.GET.get('animal_id')
    mating_date_str = request.GET.get('mating_date')
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    mating_date = datetime.strptime(mating_date_str, '%Y-%m-%d').date()
    history = BreedingRecord.objects.filter(mother=animal, status='Delivered')
    
    # Check Premium status for high-accuracy ML
    if not is_premium_user(request.user):
        return JsonResponse({'error': 'Premium Required'}, status=403)

    predicted_date, confidence, _ = BreedingPredictor.predict_birth_date(
        species=animal.species, current_parity=history.count()+1, historical_records=history, mating_date=mating_date
    )
    return JsonResponse({'predicted_date': predicted_date.strftime('%Y-%m-%d'), 'confidence': confidence})

@login_required
def profile_page(request):
    return render(request, 'health/profile.html')