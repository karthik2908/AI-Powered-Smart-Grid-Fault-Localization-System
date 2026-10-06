import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-smart-grid-fault-localization-secret-key-prod-demo'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'backend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'backend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'backend' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'security@smartgrid.local'

# Mapbox API Key auto-load from dedicated api_keys folder
MAPBOX_KEY_FILE = BASE_DIR / 'api_keys' / 'mapbox_key.txt'
if MAPBOX_KEY_FILE.exists():
    try:
        MAPBOX_API_KEY = MAPBOX_KEY_FILE.read_text(encoding='utf-8').strip()
    except Exception:
        MAPBOX_API_KEY = 'pk.eyJ1Ijoia2FydGhpa2V5YW5zazAwNCIsImEiOiJjbXV4M3VxazIwMDJrMnpzajI1Y3FtZjYwIn0.83jQBL54ebnCe9it8uSz6g'
else:
    MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY', 'pk.eyJ1Ijoia2FydGhpa2V5YW5zazAwNCIsImEiOiJjbXV4M3VxazIwMDJrMnpzajI1Y3FtZjYwIn0.83jQBL54ebnCe9it8uSz6g')

