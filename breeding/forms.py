from django import forms
from .models import BreedingRecord
from animals.models import Animal

class BreedingForm(forms.ModelForm):
    class Meta:
        model = BreedingRecord
        fields = ['animal', 'date_of_insemination', 'sire_details', 'notes']
        widgets = {
            # The 'type': 'date' triggers the nice browser calendar popup
            'date_of_insemination': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any complications or observations...'}),
            'sire_details': forms.TextInput(attrs={'placeholder': 'Tag number or name of the male...'})
        }

    def __init__(self, *args, **kwargs):
        # 1. Extract the user object from the kwargs before initializing the form
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 2. Filter the queryset safely
        if user:
            self.fields['animal'].queryset = Animal.objects.filter(
                owner=user,          # Only show this farmer's animals
                gender='Female',     # Only show females
                status='Active'      # Don't show sold or dead animals
            )
            
        self.fields['animal'].label = "Select Mother (Dam)"