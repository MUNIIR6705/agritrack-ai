import json
import base64
import requests
import re
import random
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Sum
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

# 2026 MODERN SDK
from google import genai

# Import models & ML Engine
from animals.models import Animal, WeightRecord
from breeding.models import BreedingRecord 
from breeding.ai_models import BreedingPredictor 
from .models import HealthRecord, FinanceRecord, UserProfile 

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
    """Checks if user has a confirmed 'Subscription' record in the last 30 days."""
    return FinanceRecord.objects.filter(
        user=user,
        category='Subscription',
        is_confirmed=True,
        date__gte=timezone.now() - timedelta(days=30)
    ).exists()

# --- SECURITY: EMAIL 2FA VERIFICATION ---

@login_required
@csrf_protect
def verify_2fa(request):
    """
    SECURITY NODE: Two-Factor Authentication.
    """
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'farm_name': f"{request.user.username.title()}'s Farm Node",
            'location': 'Awaiting GPS',
            'phone_number': 'N/A'
        }
    )

    if request.method == "GET":
        token = str(random.randint(100000, 999999))
        profile.login_token = token
        profile.token_created_at = timezone.now()
        profile.save()

        print("\n" + "█"*60)
        print(f"AGRITRACK SECURITY ACCESS CODE: {token}")
        print(f"USER: {request.user.username}")
        print("█"*60 + "\n")

        html_message = render_to_string('emails/auth_code.html', {
            'username': request.user.username,
            'token': token
        })

        try:
            send_mail(
                subject='AgriTrack AI: Secure Access Code',
                message=f'Your verification code is: {token}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.info(request, f"Secure access code sent to {request.user.email}")
        except Exception as e:
            messages.warning(request, "Email delivery delayed. Check terminal for backup code.")

    if request.method == "POST":
        user_code = request.POST.get('token')
        if profile.login_token == user_code and profile.is_token_valid():
            profile.login_token = None
            profile.save()
            request.session['node_verified'] = True
            messages.success(request, "Identity Verified. Synchronization active.")
            return redirect('health:health_dashboard')
        else:
            messages.error(request, "Invalid or expired security code.")
            return redirect('health:verify_2fa')

    return render(request, 'health/verify_2fa.html')

# --- DASHBOARD & HEALTH VIEWS ---

@login_required
def health_dashboard(request):
    """Intelligent Dashboard with Farm Identity Integration."""
    if not request.session.get('node_verified'):
        return redirect('health:verify_2fa')

    all_animals = Animal.objects.filter(owner=request.user)
    active_animals = all_animals.filter(status='Active')
    
    try:
        profile = request.user.health_profile
        user_display = profile.farm_name if profile.farm_name else request.user.username.title()
    except Exception:
        user_display = request.user.username.title()
    
    critical_alerts = HealthRecord.objects.filter(
        animal__owner=request.user, 
        severity='High',
        date_recorded__gte=timezone.now() - timedelta(days=3)
    ).order_by('-date_recorded')

    finance = FinanceRecord.objects.filter(user=request.user)
    income = finance.filter(transaction_type='Income', is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0
    expense = finance.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

    total_farm_value = 0
    for animal in active_animals:
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        if last_weight:
            current_price = 520 if animal.species == 'Pig' else 900
            total_farm_value += float(last_weight.weight) * current_price

    context = {
        'user_name': user_display,
        'profile': request.user.health_profile,
        'total_livestock': active_animals.count(),
        'has_animals': active_animals.exists(),
        'health_alerts': critical_alerts.count(),
        'critical_cases': critical_alerts,
        'profit': income - expense,
        'total_farm_value': total_farm_value,
        'is_premium': is_premium_user(request.user),
        'recent_searches': HealthRecord.objects.filter(animal__owner=request.user).order_by('-date_recorded')[:5],
    }
    return render(request, 'health/dashboard.html', context)

# --- IDENTITY & PROFILE MANAGEMENT ---

@login_required
def profile_page(request):
    User = get_user_model()
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'farm_name': f"{request.user.username.title()}'s Farm Node", 'location': 'Awaiting GPS', 'phone_number': 'N/A'}
    )
    
    if request.method == "POST":
        new_email = request.POST.get('email')
        verify_password = request.POST.get('verify_password')

        if new_email and new_email != request.user.email:
            if not request.user.check_password(verify_password):
                messages.error(request, "Incorrect password.")
                return redirect('health:profile_page')
            
            if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                messages.error(request, "Email already linked to another Farm Node.")
            else:
                request.user.email = new_email
                request.user.save()
                messages.success(request, "Security contact updated.")

        profile.farm_name = request.POST.get('farm_name')
        profile.location = request.POST.get('location')
        profile.phone_number = request.POST.get('phone')
        profile.primary_species = request.POST.get('primary_species')
        profile.bio = request.POST.get('bio')
        profile.save()
        messages.success(request, "Farmer Identity Synchronized.")
        return redirect('health:profile_page')

    context = {
        'profile': profile,
        'user': request.user,
        'animal_count': Animal.objects.filter(owner=request.user, status='Active').count()
    }
    return render(request, 'health/profile.html', context)

# --- SUPPLY CHAIN & MARKET MODULES ---

@login_required
def market_valuation(request):
    active_animals = Animal.objects.filter(owner=request.user, status='Active')
    PORK_PRICE, RABBIT_PRICE = 520, 900
    market_ready_nodes, growing_nodes, total_valuation = [], [], 0

    for animal in active_animals:
        last_weight_record = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        current_weight = float(last_weight_record.weight) if last_weight_record else 0
        price_rate = PORK_PRICE if animal.species == 'Pig' else RABBIT_PRICE
        valuation = current_weight * price_rate
        total_valuation += valuation

        is_ready = (animal.species == 'Pig' and current_weight >= 60) or (animal.species == 'Rabbit' and current_weight >= 2.5)
        node_data = {'animal': animal, 'weight': current_weight, 'valuation': valuation, 'is_ready': is_ready}

        if is_ready: market_ready_nodes.append(node_data)
        else: growing_nodes.append(node_data)

    return render(request, 'health/market_valuation.html', {
        'market_ready': market_ready_nodes, 'growing_nodes': growing_nodes,
        'total_valuation': total_valuation, 'pork_rate': PORK_PRICE, 'rabbit_rate': RABBIT_PRICE
    })

@login_required
def initiate_sale(request, animal_id):
    """
    Handles calculating the final sale price and automatically issuing an
    M-Pesa STK Push to the buyer's phone number.
    """
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    
    if request.method == "POST":
        buyer_phone = request.POST.get('buyer_phone')
        
        # 1. Calculate Exact Valuation based on live market rates
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        current_weight = float(last_weight.weight) if last_weight else 0
        price_rate = 520 if animal.species == 'Pig' else 900
        final_yield = current_weight * price_rate
        
        if buyer_phone:
            try:
                # 2. Format Phone Number for Daraja API (Must start with 254)
                phone = buyer_phone.strip()
                if phone.startswith('0'):
                    phone = '254' + phone[1:]
                elif phone.startswith('+'):
                    phone = phone[1:]

                # 3. Generate M-Pesa Tokens & Payload
                access_token = get_mpesa_token()
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode('utf-8')
                
                payload = {
                    "BusinessShortCode": MPESA_SHORTCODE, 
                    "Password": password, 
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline", 
                    "Amount": int(final_yield), 
                    "PartyA": phone,
                    "PartyB": MPESA_SHORTCODE, 
                    "PhoneNumber": phone, 
                    "AccountReference": f"Node_{animal.tag_number}",
                    "CallBackURL": "https://iliana-vespertine-sublabially.ngrok-free.dev/health/mpesa-callback/", 
                    "TransactionDesc": f"Livestock Purchase"
                }
                
                # 4. Execute STK Push Request
                headers = {"Authorization": f"Bearer {access_token}"}
                r = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
                response_data = r.json()
                
                # 5. Handle M-Pesa Response
                if response_data.get('ResponseCode') == '0':
                    # Success: Log pending transaction waiting for callback
                    checkout_id = response_data.get('CheckoutRequestID')
                    
                    FinanceRecord.objects.create(
                        user=request.user, 
                        transaction_type='Income', 
                        category='Livestock Sale', 
                        amount=final_yield, 
                        description=f"Pending M-Pesa payment from {phone} for Node {animal.tag_number}", 
                        checkout_request_id=checkout_id,
                        is_confirmed=False 
                    )
                    
                    # Log the animal as 'Sold' to remove it from active lists
                    animal.status = 'Sold'
                    animal.save()
                    
                    messages.success(request, f"STK Push sent! Buyer {phone} prompted to pay KES {final_yield:,.0f}.")
                else:
                    error_msg = response_data.get('errorMessage', 'Failed to initiate STK Push.')
                    messages.error(request, f"M-Pesa Error: {error_msg}")
            
            except Exception as e:
                messages.error(request, f"Payment Node Error: {str(e)}")
        else:
            messages.warning(request, "A buyer phone number is required to trigger M-Pesa.")
            
    return redirect('health:market_valuation')

# --- ENHANCED AI DIAGNOSTIC RISK ENGINE (v2.5) ---

@csrf_exempt
@login_required
def suggest_treatment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            symptoms = data.get('symptoms', '').lower()
            species = data.get('species', 'Livestock').title()
            
            knowledge_base = {
                "Pig": "African Swine Fever, PRRS, Piglet Scours, Swine Influenza, Foot and Mouth, Erysipelas.",
                "Rabbit": "Coccidiosis, Pasteurellosis, Ear Mites, RHDV, Myxomatosis."
            }

            system_instruction = (
                f"You are the AgriTrack AI Diagnostic Engine for {species}. "
                f"Reference Knowledge: {knowledge_base.get(species, 'General ailments')}. "
                "Classify symptoms into a clinical diagnosis. Output ONLY valid JSON. No markdown, no intro/outro. "
                "Schema: {\"diagnosis\": \"string\", \"severity\": \"string\", \"treatment\": \"string\", \"quarantine\": boolean, \"risk_factor\": number}"
            )

            # SWAPPED TO THE AVAILABLE HIGH-VOLUME LITE MODEL
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', 
                config={
                    'system_instruction': system_instruction, 
                    'temperature': 0.1, 
                    'response_mime_type': 'application/json'
                },
                contents=f"Farmer report: {symptoms}",
            )
            
            raw_text = response.text.strip()
            clean_json = re.sub(r'^```json\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
            
            try:
                ai_data = json.loads(clean_json)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if match:
                    ai_data = json.loads(match.group())
                else:
                    raise ValueError("Failed to locate JSON dictionary in AI response.")
            
            is_critical = ai_data.get('risk_factor', 0) >= 7
            
            return JsonResponse({
                "status": "success", 
                "diagnosis": ai_data.get('diagnosis', 'Inconclusive Classification'), 
                "treatment": ai_data.get('treatment', 'Isolate and consult local vet.'), 
                "severity": "High" if is_critical else ai_data.get('severity', 'Medium'),
                "quarantine_required": ai_data.get('quarantine', False),
                "is_critical": is_critical
            })
        except Exception as e:
            # WHITE-LABEL FIX: Only print the raw Google error to the backend console
            print(f"\n[AGRITRACK SYSTEM ERROR] => {str(e)}\n")
            
            # Send a generic, proprietary error to the frontend user so they never see "Gemini"
            return JsonResponse({
                "status": "error", 
                "message": "AgriTrack Diagnostic Engine is currently recalibrating. Please verify your symptom descriptions and try again."
            })
            
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=400)

# --- REMAINING OPERATIONAL VIEWS ---

@login_required
def animal_digital_passport(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    return render(request, 'health/animal_passport.html', {
        'animal': animal,
        'health_history': HealthRecord.objects.filter(animal=animal).order_by('-date_recorded'),
        'weight_history': WeightRecord.objects.filter(animal=animal).order_by('-date_recorded'),
    })

@login_required
def market_hub(request):
    if not is_premium_user(request.user):
        messages.warning(request, "Premium feature required.")
        return redirect('health:upgrade_subscription')
    active_animals = Animal.objects.filter(owner=request.user, status='Active')
    market_ready_stock = []
    for animal in active_animals:
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        if last_weight and ( (animal.species == 'Pig' and last_weight.weight >= 60) or (animal.species == 'Rabbit' and last_weight.weight >= 2.5) ):
            market_ready_stock.append({'animal': animal, 'weight': last_weight.weight, 'uep': animal.uep_code})
    return render(request, 'health/market_hub.html', {'ready_stock': market_ready_stock})

@login_required
def add_transaction(request):
    if request.method == "POST":
        try:
            payment_method = request.POST.get('payment_method')
            if payment_method == 'M-Pesa':
                access_token = get_mpesa_token()
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode('utf-8')
                phone = f"254{request.POST.get('mpesa_number')[-9:]}"
                
                payload = {
                    "BusinessShortCode": MPESA_SHORTCODE, 
                    "Password": password, 
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline", 
                    "Amount": int(float(request.POST.get('amount'))), 
                    "PartyA": phone,
                    "PartyB": MPESA_SHORTCODE, 
                    "PhoneNumber": phone, 
                    "AccountReference": "AgriTrackAI",
                    "CallBackURL": "https://iliana-vespertine-sublabially.ngrok-free.dev/health/mpesa-callback/", 
                    "TransactionDesc": "SaaS Subscription"
                }
                
                r = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers={"Authorization": f"Bearer {access_token}"})
                FinanceRecord.objects.create(user=request.user, transaction_type=request.POST.get('type'), category=request.POST.get('category'), amount=request.POST.get('amount'), checkout_request_id=r.json().get('CheckoutRequestID'), description=request.POST.get('description'))
                messages.success(request, "M-Pesa Push Sent.")
            else:
                FinanceRecord.objects.create(user=request.user, transaction_type=request.POST.get('type'), category=request.POST.get('category'), amount=request.POST.get('amount'), description=request.POST.get('description'), is_confirmed=True)
                messages.success(request, "Recorded.")
            return redirect('health:financial_reports')
        except Exception as e:
            messages.error(request, f"Finance Node Error: {str(e)}")
    return render(request, 'health/add_transaction.html')

@login_required
def financial_reports(request):
    records = FinanceRecord.objects.filter(user=request.user).order_by('-date')
    income = records.filter(transaction_type='Income', is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0
    expense = records.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'health/financial_reports.html', {'records': records, 'income': income, 'expense': expense, 'profit': income - expense})

@login_required
def add_health_record(request):
    if request.method == "POST":
        animal = get_object_or_404(Animal, id=request.POST.get('animal'), owner=request.user)
        HealthRecord.objects.create(animal=animal, symptoms=request.POST.get('symptoms'), severity=request.POST.get('severity'), diagnosis=request.POST.get('diagnosis'), treatment=request.POST.get('treatment'))
        messages.success(request, "Health record archived.")
        return redirect('health:health_dashboard')
    return render(request, 'health/add_health_record.html', {'animals': Animal.objects.filter(owner=request.user, status='Active')})

@login_required
def record_weight(request):
    if request.method == "POST":
        animal = get_object_or_404(Animal, id=request.POST.get('animal'), owner=request.user)
        WeightRecord.objects.create(animal=animal, weight=request.POST.get('weight'))
        messages.success(request, "Weight logged.")
        return redirect('health:health_dashboard')
    return render(request, 'health/record_weight.html', {'animals': Animal.objects.filter(owner=request.user, status='Active'), 'preselected_id': request.GET.get('animal')})

@login_required
def upgrade_subscription(request):
    return render(request, 'health/upgrade.html')

@csrf_exempt
def mpesa_callback(request):
    """Listens for Safaricom's final response after the user enters their PIN."""
    if request.method == "POST":
        try:
            callback_data = json.loads(request.body)
            stk_callback = callback_data['Body']['stkCallback']
            
            result_code = stk_callback['ResultCode']
            checkout_id = stk_callback['CheckoutRequestID']
            result_desc = stk_callback.get('ResultDesc', 'No description provided')
            
            # Find the pending transaction in the database
            record = FinanceRecord.objects.filter(checkout_request_id=checkout_id).first()
            
            if record:
                if result_code == 0:
                    # SUCCESS: User entered PIN and had funds
                    record.is_confirmed = True
                    record.description = f"Successful: {record.description}"
                    record.save()
                else:
                    # FAILED: User cancelled, timed out, or insufficient funds
                    record.is_confirmed = False
                    record.description = f"Failed: {result_desc}"
                    record.save()
                    
                    # Revert the animal back to "Active" on the market since the sale failed!
                    match = re.search(r'Node ([\w-]+)', record.description)
                    if match:
                        Animal.objects.filter(tag_number=match.group(1)).update(status='Active')

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback Accepted"})
        except Exception as e:
            print(f"M-PESA CALLBACK ERROR: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error Processing Callback"})
            
    return JsonResponse({"status": "invalid method"})

@login_required
def predict_gestation_api(request):
    animal = get_object_or_404(Animal, id=request.GET.get('animal_id'), owner=request.user)
    mating_date = datetime.strptime(request.GET.get('mating_date'), '%Y-%m-%d').date()
    p_date, conf, _ = BreedingPredictor.predict_birth_date(animal.species, 1, [], mating_date)
    return JsonResponse({'predicted_date': p_date.strftime('%Y-%m-%d'), 'confidence': conf})


# --- NEW: DIGITAL QR RECEIPT VIEW ---
def diagnostic_receipt(request, animal_id):
    """
    Public endpoint hit when a vet scans the printed PDF QR Code.
    Displays a mobile-friendly view of the animal's latest diagnostic record.
    """
    animal = get_object_or_404(Animal, id=animal_id)
    
    # Get the most recent health diagnostic for this animal
    latest_record = HealthRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
    
    # Safely get the farm name
    try:
        farm_name = animal.owner.health_profile.farm_name
    except Exception:
        farm_name = f"{animal.owner.username.title()}'s Farm"
        
    context = {
        'animal': animal,
        'record': latest_record,
        'farm_name': farm_name
    }
    
    return render(request, 'health/diagnostic_receipt.html', context)