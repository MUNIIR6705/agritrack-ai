from django.contrib import admin
from .models import AITrainingData, HealthRecord, FinanceRecord

# --- SMART AI TRAINING DATA ---
@admin.register(AITrainingData)
class AITrainingDataAdmin(admin.ModelAdmin):
    # Displays the disease, symptoms, and severity at a glance
    list_display = ('diagnosis', 'severity', 'symptoms_preview')
    list_filter = ('severity',)
    search_fields = ('diagnosis', 'symptoms')

    def symptoms_preview(self, obj):
        return obj.symptoms[:50] + "..." if len(obj.symptoms) > 50 else obj.symptoms
    symptoms_preview.short_description = 'Symptoms'

# --- ANIMAL HEALTH RECORDS ---
@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    # Shows which animal is sick and what the AI suggested
    list_display = ('animal', 'diagnosis', 'severity', 'date_recorded')
    list_filter = ('severity', 'date_recorded')
    search_fields = ('animal__tag_number', 'diagnosis')

# --- M-PESA ENABLED FINANCIAL RECORDS ---
@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    # Highlights M-Pesa transactions and total cash flow
    list_display = ('date', 'transaction_type', 'category', 'amount', 'short_description')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('description', 'category')

    def short_description(self, obj):
        return obj.description[:40] + "..." if len(obj.description) > 40 else obj.description
    short_description.short_description = 'Details'

# --- USER PROFILE MANAGEMENT ---
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'location', 'phone_number', 'primary_species', 'updated_at')
    search_fields = ('user__username', 'farm_name', 'location', 'phone_number')
    list_filter = ('primary_species',)

# --- SEARCH & ANALYTICS (Optional) ---
# If you decide to track what the AI is being asked most often
# @admin.register(SearchAnalytics)
# class SearchAnalyticsAdmin(admin.ModelAdmin):
#     list_display = ('timestamp', 'query_text', 'found_match')