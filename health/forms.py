from django import forms
from .models import HealthRecord

class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = ['animal', 'symptoms', 'diagnosis', 'treatment', 'severity', 'cost']
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 2}),
            'treatment': forms.Textarea(attrs={'rows': 2}),
        }