from django.contrib import admin
from .models import BreedingRecord

@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    # Updated to match the actual fields in your model
    list_display = ('mother', 'mating_date', 'expected_delivery', 'status', 'litter_size')
    list_filter = ('status', 'mating_date', 'mother__species')
    search_fields = ('mother__tag_number', 'father_tag')
    readonly_fields = ('expected_delivery',)