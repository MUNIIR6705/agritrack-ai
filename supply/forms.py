from django import forms
from .models import SaleListing

class SaleForm(forms.ModelForm):
    class Meta:
        model = SaleListing
        fields = ['price', 'status']
        widgets = {
            'price': forms.NumberInput(attrs={'placeholder': 'Enter Price in KES'}),
        }