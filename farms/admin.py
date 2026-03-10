from django.contrib import admin
from .models import Farm

class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location', 'size_acres')
    search_fields = ('name', 'location')

admin.site.register(Farm, FarmAdmin)