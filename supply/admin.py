from django.contrib import admin
from .models import Supply

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'supply_type', 'quantity', 'unit', 'min_stock_level', 'last_updated')
    list_filter = ('supply_type',)
    search_fields = ('name',)