import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Animal, WeightRecord
from .forms import AnimalForm, WeightForm

@login_required
def animal_list(request):
    """Fetches all active animals owned by the logged-in farmer"""
    # Filter by owner and sort so newest additions appear first
    animals = Animal.objects.filter(owner=request.user).order_by('-id')
    return render(request, 'animals/animal_list.html', {'animals': animals})

@login_required
def animal_detail(request, animal_id):
    """Detailed view of a single animal including health and weight history"""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    return render(request, 'animals/animal_detail.html', {'animal': animal})

@login_required
def add_animal(request):
    """Front-end view for farmers to register new livestock"""
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.owner = request.user # Automated ownership assignment
            animal.save()
            messages.success(request, f"Animal {animal.tag_number} registered successfully!")
            # FIXED: Added 'animals:' namespace
            return redirect('animals:animal_list') 
    else:
        form = AnimalForm()
        
    return render(request, 'animals/add_animal.html', {'form': form})

@login_required
def add_weight(request, animal_id):
    """Records new weight data and updates the animal's current weight"""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    
    if request.method == 'POST':
        form = WeightForm(request.POST, user=request.user)
        if form.is_valid():
            weight_record = form.save(commit=False)
            weight_record.animal = animal
            weight_record.save()
            
            # Smart update: Sync current weight back to the Animal model
            animal.weight = weight_record.weight
            animal.save()
            
            messages.success(request, f"Weight of {weight_record.weight}kg logged for {animal.tag_number}.")
            # FIXED: Added 'animals:' namespace
            return redirect('animals:animal_detail', animal_id=animal.id)
    else:
        form = WeightForm(initial={'animal': animal}, user=request.user)
        
    return render(request, 'animals/add_weight.html', {'form': form, 'animal': animal})

@login_required
def sell_animal(request, animal_id):
    """Smart Sales: Archives the animal and prepares data for financial logging"""
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)

    if animal.status == 'Sold':
        messages.warning(request, f"{animal.tag_number} is already marked as Sold.")
        # FIXED: Added 'animals:' namespace
        return redirect('animals:animal_detail', animal_id=animal.id)

    if request.method == "POST":
        sale_price = request.POST.get('sale_price')
        buyer_name = request.POST.get('buyer_name')
        
        try:
            animal.status = 'Sold'
            animal.save()

            # Note: Integration with health:financial_reports could happen here
            messages.success(request, f"🎉 Sale Confirmed! {animal.tag_number} sold to {buyer_name} for KES {sale_price}.")
            # FIXED: Added 'animals:' namespace
            return redirect('animals:animal_list')

        except Exception as e:
            messages.error(request, f"Error processing sale: {str(e)}")

    days_on_farm = "Unknown"
    if animal.date_of_birth:
        days_on_farm = (timezone.now().date() - animal.date_of_birth).days

    context = {
        'animal': animal,
        'days_on_farm': days_on_farm
    }
    return render(request, 'animals/sell_animal.html', context)