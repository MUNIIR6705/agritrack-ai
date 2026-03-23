from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# --- PYMYSQL MONKEYPATCH (RAILWAY FIX) ---
# This forces Django to use the pure-Python PyMySQL driver instead of the 
# C-based mysqlclient, completely bypassing the "missing libmariadb.so.3" error.
import pymysql
# Give PyMySQL a "Fake ID" so Django thinks it is version 2.2.1
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
# -----------------------------------------

# Load environment variables from the .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    '.herokuapp.com', 
    '.railway.app', 
    '.ondigitalocean.app',
    '.ngrok-free.dev',  # Safaricom Callback access
    '*'                 # Dev override
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app', # <-- THIS IS THE FIX FOR YOUR DASHBOARD LOGIN!
    'https://*.herokuapp.com',
    'https://*.ngrok-free.dev'  # CRITICAL: Allows M-Pesa POST requests
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
    'anymail',  # <-- Added the required comma here!
    
    # AgriTrack Core Apps
    'users',
    'farms.apps.FarmsConfig',
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
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=False 
    )
}

# --- EMAIL CONFIGURATION (Resend HTTP API) ---
# Sends emails securely over HTTP to bypass cloud server port blocks.
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

ANYMAIL = {
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
}

# CRITICAL: Because you are on the free tier and haven't bought a domain yet,
# Resend REQUIRES you to send emails from this exact onboarding address.
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"


# --- SESSION & SECURITY POLICIES ---
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  
SESSION_SAVE_EVERY_REQUEST = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise Optimization for Production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- AGRI-TRACK AI & EXTERNAL APIS ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_CX = os.environ.get('GOOGLE_SEARCH_CX')

# M-PESA DARAJA API CONFIG
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
MPESA_ENVIRONMENT = 'sandbox' 
# Required for Daraja Callbacks
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL')

# --- PRODUCTION SECURITY SETTINGS ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# --- PROJECT DEFAULTS ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi' 
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

# Crispy Forms Config
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- AUTHENTICATION REDIRECTS ---
LOGIN_URL = 'login' 
LOGIN_REDIRECT_URL = 'health:health_dashboard'
LOGOUT_REDIRECT_URL = 'login'