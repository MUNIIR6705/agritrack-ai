from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supply

@login_required
def inventory_list(request):
    """View all farm supplies and stock levels"""
    supplies = Supply.objects.all().order_by('supply_type', 'name')
    return render(request, 'supply/inventory.html', {'supplies': supplies})

@login_required
def add_supply(request):
    """Add a new supply item or restock"""
    if request.method == "POST":
        name = request.POST.get('name')
        s_type = request.POST.get('supply_type')
        qty = request.POST.get('quantity')
        unit = request.POST.get('unit')
        min_level = request.POST.get('min_stock_level')

        Supply.objects.create(
            name=name,
            supply_type=s_type,
            quantity=qty,
            unit=unit,
            min_stock_level=min_level
        )
        messages.success(request, f"Added {name} to inventory.")
        return redirect('inventory_list')
        
    return render(request, 'supply/add_supply.html')