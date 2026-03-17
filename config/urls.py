from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Views from various modules
from health import views as health_views
from users import views as user_views

admin.site.site_header = "AgriTrack AI System"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Authentication System & Landing Page ---
    # FIXED: template_name updated from 'landing_page.html' to 'landing.html'
    
    # 1. This makes your informative landing page the Root (Home) Page
    path('', auth_views.LoginView.as_view(template_name='landing.html'), name='login'),
    
    # 2. Keep the /login/ path pointing to the same place for consistency
    path('login/', auth_views.LoginView.as_view(template_name='landing.html'), name='login_redirect'),
    
    path('register/', user_views.register, name='register'),
    path('logout/', user_views.custom_logout, name='logout'),
    
    # Post-login role handler
    path('login_success/', user_views.login_success, name='login_redirect_handler'),

    # --- Application Module Routes ---
    path('health/', include('health.urls')),
    path('breeding/', include('breeding.urls')),
    path('animals/', include('animals.urls')),
    path('supply/', include('supply.urls')),
    path('reports/', include('reports.urls')),
    path('farms/', include('farms.urls')), 

    # --- Dashboard Rerouting ---
    path('dashboard/', RedirectView.as_view(pattern_name='health:health_dashboard', permanent=True)),
    
    # Pointing to the profile view
    path('profile/', health_views.profile_page, name='profile_page'),
]

# Serving Media and Static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)