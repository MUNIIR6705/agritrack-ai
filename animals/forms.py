from django import forms
from .models import Animal, WeightRecord

class AnimalForm(forms.ModelForm):
    """Form for farmers to register new livestock with full dropdown support"""
    class Meta:
        model = Animal
        # Fields mapped to the Animal model
        fields = ['tag_number', 'species', 'breed', 'date_of_birth', 'gender', 'status']
        
        widgets = {
            'tag_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., AG-102'
            }),
            'species': forms.Select(attrs={
                'class': 'form-select'
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Large White / Californian'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class WeightForm(forms.ModelForm):
    """Form for recording weight with user-specific animal filtering"""
    class Meta:
        model = WeightRecord
        fields = ['animal', 'weight', 'notes']
        
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': 'Enter weight in KG'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Observations (e.g., healthy appetite)'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Retrieve the user passed from the view
        user = kwargs.pop('user', None)
        super(WeightForm, self).__init__(*args, **kwargs)
        
        # Security & UX: Only show animals belonging to the logged-in farmer
        if user:
            self.fields['animal'].queryset = Animal.objects.filter(
                owner=user, 
                status='Active'
            ).order_by('tag_number')