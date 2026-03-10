from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def profile(request):
    return render(request, 'users/profile.html')

# --- THE TRAFFIC COP VIEW ---
def login_success(request):
    """
    Redirects users based on their role.
    Superusers -> Admin Panel
    Farmers -> Dashboard
    """
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')
    else:
        return redirect('dashboard')