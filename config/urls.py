from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Views from various modules
from health import views as health_views
from users import views as user_views
from farms import views as farm_views  # New import for the Farmer Dashboard

admin.site.site_header = "AgriTrack AI System"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Authentication System ---
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', user_views.custom_logout, name='logout'),
    
    # Post-login role handler
    path('login_success/', user_views.login_success, name='login_redirect'),

    # --- Application Module Routes ---
    path('health/', include('health.urls')),
    path('breeding/', include('breeding.urls')),
    path('animals/', include('animals.urls')),
    path('supply/', include('supply.urls')),
    path('reports/', include('reports.urls')),
    path('farms/', include('farms.urls')),  # Crucial for AJAX weather refresh

    # --- The Main Dashboard ---
    # We now point this to the farm_views dashboard which has the Weather/AI logic
    path('dashboard/', farm_views.farmer_dashboard, name='dashboard'),
    
    # Pointing to the profile view
    path('profile/', health_views.profile_page, name='profile_page'),
    
    # --- Root Redirect ---
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

# Serving Media and Static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Using STATIC_ROOT for static files if STATICFILES_DIRS is empty
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)