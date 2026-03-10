from pathlib import Path
import os
import dj_database_url  # Standard for 2026 Production deployments

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# In production, this MUST be set in your environment variables
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-replace-in-prod')

# DEBUG should be False in production
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Domains allowed for deployment - Added wildcard for dynamic cloud subdomains
ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    '.herokuapp.com', 
    '.pythonanywhere.com', 
    '.railway.app', 
    '.ondigitalocean.app'
]

# --- APP DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    
    # Third Party
    'crispy_forms',
    'crispy_bootstrap5',
    
    # My Apps (AgriTrack Core)
    'users',
    'farms',
    'animals',
    'breeding',
    'health',
    'supply',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'farms.context_processors.notifications', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- DATABASE CONFIGURATION ---
# Uses local MySQL if DATABASE_URL is not found (Development mode)
DATABASES = {
    'default': dj_database_url.config(
        default='mysql://root:Ramakokha06!@127.0.0.1:3306/agritrack_db',
        conn_max_age=600,
        ssl_require=not DEBUG # Require SSL for DB in production
    )
}

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Production-ready static storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- AGRI-TRACK AI & EXTERNAL APIS ---
# Always pull from OS Environment for safety
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyByribUmU7oMt95sCdiSnj2ajJ6f9nA6qg')
GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY', '')
GOOGLE_SEARCH_CX = os.environ.get('GOOGLE_SEARCH_CX', '')

# M-PESA DARAJA API (Production Sandbox)
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'QGMx3AcyyFcGVak4ra4UMAQpA6Isv9arqU0VR7em9WdG7rXF')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'QMlsZXHiclPuiehFi6WMLbSObvMifnL7A9j5JzGbr83BE09kyzrRyag1gV8cLUnN')
MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_ENVIRONMENT = 'sandbox' 

# --- PRODUCTION SECURITY SETTINGS ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # 1 Year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Standard Django Defaults
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi' 
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_REDIRECT_URL = 'health:health_dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'