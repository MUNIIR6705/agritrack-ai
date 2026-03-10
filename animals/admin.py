from django.contrib import admin
from .models import Animal, WeightRecord

class AnimalAdmin(admin.ModelAdmin):
    list_display = ('tag_number', 'species', 'gender', 'status')
    list_filter = ('species', 'status')
    search_fields = ('tag_number',)

admin.site.register(Animal, AnimalAdmin)
admin.site.register(WeightRecord)