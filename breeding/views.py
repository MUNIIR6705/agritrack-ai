from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse 
from animals.models import Animal
from .models import BreedingRecord
from .ai_models import BreedingPredictor
from datetime import datetime

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
        
        # 1. Fetch the ACTUAL records so the ML model can calculate gestation days
        history = BreedingRecord.objects.filter(mother=animal, status='Delivered').order_by('mating_date')
        
        # 2. Determine current parity (1st birth, 2nd birth, etc.)
        parity = history.count() + 1

        # 3. Call the ML Engine with correct arguments
        predicted_date, confidence, predicted_days = BreedingPredictor.predict_birth_date(
            species=animal.species,
            current_parity=parity,
            historical_records=history, # Pass the QuerySet, not just a count
            mating_date=mating_date
        )

        return JsonResponse({
            'predicted_date': predicted_date.strftime('%Y-%m-%d'),
            'formatted_date': predicted_date.strftime('%b %d, %Y'),
            'days': predicted_days,
            'confidence': confidence # This now returns the ML status string
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

            # Re-run ML logic for final save
            history = BreedingRecord.objects.filter(mother=animal, status='Delivered').order_by('mating_date')
            parity = history.count() + 1
            
            predicted_date, _, _ = BreedingPredictor.predict_birth_date(
                species=animal.species,
                current_parity=parity,
                historical_records=history,
                mating_date=mating_date
            )

            BreedingRecord.objects.create(
                mother=animal,
                mating_date=mating_date,
                expected_delivery=predicted_date,
                father_tag=sire,
                status='Pregnant'
            )

            messages.success(request, f"🚀 AI Forecast Saved! Due on {predicted_date.strftime('%b %d, %Y')}")
            return redirect('breeding:breeding_list')

        except Exception as e:
            messages.error(request, f"System Error: {str(e)}")
            return redirect('breeding:add_breeding')

    animals = Animal.objects.filter(
        owner=request.user, 
        status='Active', 
        gender__iexact='Female',
        species__iregex=r'(pig|rabbit)'
    )
    return render(request, 'breeding/breeding_form.html', {'animals': animals})

@login_required
def mark_delivered(request, record_id):
    """Updates record status when birth occurs."""
    record = get_object_or_404(BreedingRecord, id=record_id, mother__owner=request.user)
    record.status = 'Delivered'
    record.actual_delivery = timezone.now().date()
    record.save()
    messages.success(request, f"Birth recorded for {record.mother.tag_number}.")
    return redirect('breeding:breeding_list')