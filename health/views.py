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

# Import models & Forms (Ensure your app structures match these imports)
from animals.models import Animal, WeightRecord
from animals.forms import AnimalForm, WeightForm
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

# ==========================================
# SECTION 1: SECURITY & IDENTITY
# ==========================================

@login_required
@csrf_protect
def verify_2fa(request):
    """SECURITY NODE: Two-Factor Authentication."""
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


# ==========================================
# SECTION 2: DASHBOARD & ANIMAL ROSTER
# ==========================================

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

@login_required
def animal_list(request):
    """Fetches all active animals owned by the logged-in farmer"""
    animals = Animal.objects.filter(owner=request.user).order_by('-id')
    return render(request, 'animals/animal_list.html', {'animals': animals})

@login_required
def animal_detail(request, animal_id):
    """Detailed view of a single animal including health and weight history"""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    weight_history = animal.weight_records.all().order_by('-date_recorded')
    context = {
        'animal': animal,
        'weight_history': weight_history,
        'today': timezone.now().date()
    }
    return render(request, 'animals/animal_detail.html', context)

@login_required
def add_animal(request):
    """Front-end view for farmers to register new livestock"""
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.owner = request.user 
            animal.save() 
            messages.success(request, f"Animal {animal.tag_number} registered successfully!")
            return redirect('animals:animal_list') 
    else:
        form = AnimalForm()
    return render(request, 'animals/add_animal.html', {'form': form})

# ==========================================
# SECTION 3: BREEDING & AI GESTATION
# ==========================================

@login_required
def breeding_list(request):
    """Main console for Breeding & Births."""
    all_records = BreedingRecord.objects.filter(mother__owner=request.user).order_by('-expected_delivery')
    expecting_count = all_records.filter(status='Pregnant').count()
    overdue_date = timezone.now().date()
    overdue_count = all_records.filter(status='Pregnant', expected_delivery__lt=overdue_date).count()
    recent_births = all_records.filter(status='Delivered').count()

    return render(request, 'breeding/breeding_list.html', {
        'records': all_records,
        'expecting_count': expecting_count,
        'overdue_count': overdue_count,
        'recent_births': recent_births,
        'today': overdue_date
    })

@login_required
def predict_gestation_api(request):
    """AJAX endpoint to run ML prediction before saving."""
    animal_id = request.GET.get('animal_id')
    mating_date_str = request.GET.get('mating_date')
    
    if not animal_id or not mating_date_str:
        return JsonResponse({'error': 'Missing data'}, status=400)

    try:
        animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
        mating_date = datetime.strptime(mating_date_str, '%Y-%m-%d').date()
        history = BreedingRecord.objects.filter(mother=animal, status='Delivered').order_by('mating_date')
        parity = history.count() + 1

        predicted_date, confidence, predicted_days = BreedingPredictor.predict_birth_date(
            species=animal.species, current_parity=parity, historical_records=history, mating_date=mating_date
        )

        return JsonResponse({
            'predicted_date': predicted_date.strftime('%Y-%m-%d'),
            'formatted_date': predicted_date.strftime('%b %d, %Y'),
            'days': predicted_days,
            'confidence': confidence
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def add_breeding(request):
    """AI-Powered Mating Logger."""
    if request.method == "POST":
        animal_id = request.POST.get('animal')
        mating_date_str = request.POST.get('mating_date')
        sire = request.POST.get('sire', '')

        try:
            animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
            mating_date = datetime.strptime(mating_date_str, '%Y-%m-%d').date()
            history = BreedingRecord.objects.filter(mother=animal, status='Delivered').order_by('mating_date')
            parity = history.count() + 1
            
            predicted_date, _, _ = BreedingPredictor.predict_birth_date(
                species=animal.species, current_parity=parity, historical_records=history, mating_date=mating_date
            )

            BreedingRecord.objects.create(
                mother=animal, mating_date=mating_date, expected_delivery=predicted_date,
                father_tag=sire, status='Pregnant'
            )

            messages.success(request, f"🚀 AI Forecast Saved! Due on {predicted_date.strftime('%b %d, %Y')}")
            return redirect('breeding:breeding_list')

        except Exception as e:
            messages.error(request, f"System Error: {str(e)}")
            return redirect('breeding:add_breeding')

    animals = Animal.objects.filter(owner=request.user, status='Active', gender__iexact='Female', species__iregex=r'(pig|rabbit)')
    return render(request, 'breeding/breeding_form.html', {'animals': animals})

@login_required
def mark_delivered(request, record_id):
    """Updates record status when birth occurs AND auto-generates the babies."""
    record = get_object_or_404(BreedingRecord, id=record_id, mother__owner=request.user)
    
    if request.method == "POST":
        try:
            litter_size = int(request.POST.get('litter_size', 1))
        except ValueError:
            litter_size = 1

        record.status = 'Delivered'
        record.actual_delivery = timezone.now().date()
        record.save()
        
        babies_created = 0
        for _ in range(litter_size):
            Animal.objects.create(
                species=record.mother.species, 
                breed=record.mother.breed, 
                date_of_birth=record.actual_delivery, 
                gender='Unknown', 
                owner=request.user,
                status='Active',
                mother=record.mother # Links baby to the mother's Offspring list
            )
            babies_created += 1

        if babies_created > 0:
            messages.success(request, f"🎉 Mother {record.mother.tag_number} delivered. {babies_created} newborn(s) auto-tagged!")
        else:
            messages.success(request, f"Birth recorded for {record.mother.tag_number}.")
            
        return redirect('breeding:breeding_list')

    return render(request, 'breeding/confirm_delivery.html', {'record': record})


# ==========================================
# SECTION 4: HEALTH & AI DIAGNOSTICS
# ==========================================

@csrf_exempt
@login_required
def suggest_treatment(request):
    """AI Diagnostic Risk Engine (v2.5)"""
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

            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', 
                config={'system_instruction': system_instruction, 'temperature': 0.1, 'response_mime_type': 'application/json'},
                contents=f"Farmer report: {symptoms}",
            )
            
            raw_text = response.text.strip()
            clean_json = re.sub(r'^```json\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
            
            try:
                ai_data = json.loads(clean_json)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if match: ai_data = json.loads(match.group())
                else: raise ValueError("Failed to locate JSON dictionary in AI response.")
            
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
            print(f"\n[AGRITRACK SYSTEM ERROR] => {str(e)}\n")
            return JsonResponse({
                "status": "error", 
                "message": "AgriTrack Diagnostic Engine is currently recalibrating. Please verify your symptom descriptions and try again."
            })
            
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=400)

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
    """Records new weight data and attaches it to the animal's history"""
    animal_id = request.GET.get('animal') or request.POST.get('animal')
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    
    if request.method == 'POST':
        form = WeightForm(request.POST, user=request.user)
        if form.is_valid():
            weight_record = form.save(commit=False)
            weight_record.animal = animal
            weight_record.save()
            messages.success(request, f"Weight of {weight_record.weight}kg logged for {animal.tag_number}.")
            return redirect('animals:animal_detail', animal_id=animal.id)
    else:
        form = WeightForm(initial={'animal': animal}, user=request.user)
        
    return render(request, 'animals/add_weight.html', {'form': form, 'animal': animal})

def diagnostic_receipt(request, animal_id):
    """Public endpoint hit when a vet scans the printed PDF QR Code."""
    animal = get_object_or_404(Animal, id=animal_id)
    latest_record = HealthRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
    try:
        farm_name = animal.owner.health_profile.farm_name
    except Exception:
        farm_name = f"{animal.owner.username.title()}'s Farm"
        
    return render(request, 'health/diagnostic_receipt.html', {
        'animal': animal, 'record': latest_record, 'farm_name': farm_name
    })

@login_required
def animal_digital_passport(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    return render(request, 'health/animal_passport.html', {
        'animal': animal,
        'health_history': HealthRecord.objects.filter(animal=animal).order_by('-date_recorded'),
        'weight_history': WeightRecord.objects.filter(animal=animal).order_by('-date_recorded'),
    })


# ==========================================
# SECTION 5: FINANCE & M-PESA
# ==========================================

@login_required
def financial_reports(request):
    records = FinanceRecord.objects.filter(user=request.user).order_by('-date')
    income = records.filter(transaction_type='Income', is_confirmed=True).aggregate(Sum('amount'))['amount__sum'] or 0
    expense = records.filter(transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'health/financial_reports.html', {'records': records, 'income': income, 'expense': expense, 'profit': income - expense})

@login_required
def add_transaction(request):
    """Logs Finance records and triggers M-Pesa STK push for digital payments."""
    if request.method == "POST":
        try:
            payment_method = request.POST.get('payment_method')
            amount = float(request.POST.get('amount', 0))
            
            if payment_method == 'M-Pesa':
                access_token = get_mpesa_token()
                if not access_token:
                    messages.error(request, "Failed to connect to M-Pesa. Please try again.")
                    return redirect('health:add_transaction')
                    
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password_str = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
                password = base64.b64encode(password_str.encode()).decode('utf-8')
                
                raw_phone = request.POST.get('mpesa_number', '').strip().replace('+', '')
                phone = f"254{raw_phone[1:]}" if raw_phone.startswith('0') else f"254{raw_phone[-9:]}"
                
                # IMPORTANT: Define your NGROK_URL in settings.py!
                base_url = getattr(settings, 'NGROK_URL', 'https://placeholder.ngrok-free.app')
                callback_url = f"{base_url}/health/mpesa-callback/"
                
                payload = {
                    "BusinessShortCode": MPESA_SHORTCODE, 
                    "Password": password, 
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline", 
                    "Amount": int(amount), 
                    "PartyA": phone,
                    "PartyB": MPESA_SHORTCODE, 
                    "PhoneNumber": phone, 
                    "AccountReference": "AgriTrackAI",
                    "CallBackURL": callback_url, 
                    "TransactionDesc": "SaaS Subscription"[:13] 
                }
                
                headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
                r = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
                response_data = r.json()
                
                if response_data.get('ResponseCode') == '0':
                    FinanceRecord.objects.create(
                        user=request.user, 
                        transaction_type=request.POST.get('type'), 
                        category=request.POST.get('category'), 
                        amount=amount, 
                        checkout_request_id=response_data.get('CheckoutRequestID'), 
                        description=f"Pending: {request.POST.get('description')}",
                        is_confirmed=False 
                    )
                    messages.success(request, f"M-Pesa Push Sent! Please check phone {phone} to pay KES {int(amount)}.")
                else:
                    error_msg = response_data.get('errorMessage', 'Failed to initiate STK Push.')
                    messages.error(request, f"M-Pesa Error: {error_msg}")
                    return redirect('health:add_transaction')
            else:
                FinanceRecord.objects.create(
                    user=request.user, transaction_type=request.POST.get('type'), 
                    category=request.POST.get('category'), amount=amount, 
                    description=request.POST.get('description'), is_confirmed=True 
                )
                messages.success(request, "Manual transaction recorded successfully.")
                
            return redirect('health:financial_reports')
            
        except Exception as e:
            messages.error(request, f"Finance Node Error: {str(e)}")
            return redirect('health:add_transaction')
            
    return render(request, 'health/add_transaction.html')

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
                    
                    # If this was a livestock sale, revert the animal back to "Active"
                    match = re.search(r'Node ([\w-]+)', record.description)
                    if match:
                        Animal.objects.filter(tag_number=match.group(1)).update(status='Active')

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback Accepted"})
        except Exception as e:
            print(f"M-PESA CALLBACK ERROR: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error Processing Callback"})
            
    return JsonResponse({"status": "invalid method"})

# ==========================================
# SECTION 6: MARKET & VALUATION
# ==========================================

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
    """Calculates sale price and auto-issues M-Pesa STK Push to buyer."""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    
    if request.method == "POST":
        buyer_phone = request.POST.get('buyer_phone')
        last_weight = WeightRecord.objects.filter(animal=animal).order_by('-date_recorded').first()
        current_weight = float(last_weight.weight) if last_weight else 0
        price_rate = 520 if animal.species == 'Pig' else 900
        final_yield = current_weight * price_rate
        
        if buyer_phone:
            try:
                phone = buyer_phone.strip()
                if phone.startswith('0'): phone = '254' + phone[1:]
                elif phone.startswith('+'): phone = phone[1:]

                access_token = get_mpesa_token()
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode('utf-8')
                
                base_url = getattr(settings, 'NGROK_URL', 'https://placeholder.ngrok-free.app')
                callback_url = f"{base_url}/health/mpesa-callback/"
                
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
                    "CallBackURL": callback_url, 
                    "TransactionDesc": f"Livestock Purchase"
                }
                
                headers = {"Authorization": f"Bearer {access_token}"}
                r = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
                response_data = r.json()
                
                if response_data.get('ResponseCode') == '0':
                    checkout_id = response_data.get('CheckoutRequestID')
                    FinanceRecord.objects.create(
                        user=request.user, transaction_type='Income', category='Livestock Sale', 
                        amount=final_yield, description=f"Pending M-Pesa payment from {phone} for Node {animal.tag_number}", 
                        checkout_request_id=checkout_id, is_confirmed=False 
                    )
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

@login_required
def upgrade_subscription(request):
    return render(request, 'health/upgrade.html')