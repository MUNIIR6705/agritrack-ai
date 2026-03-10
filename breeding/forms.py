from django import forms
from .models import BreedingRecord
from animals.models import Animal

class BreedingForm(forms.ModelForm):
    class Meta:
        model = BreedingRecord
        fields = ['animal', 'date_of_insemination', 'sire_details', 'notes']
        widgets = {
            'date_of_insemination': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].queryset = Animal.objects.all()
        self.fields['animal'].label = "Select Animal"