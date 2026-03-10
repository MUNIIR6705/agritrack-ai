from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Get the custom user model
User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Added 'image' to the fields list so the form expects it
        fields = ['image', 'farm_name', 'phone', 'location', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }