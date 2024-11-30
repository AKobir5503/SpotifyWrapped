from pathlib import Path
import os
from decouple import config
import django_heroku
import dj_database_url

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Variables
SECRET_KEY = config('SECRET_KEY', default='your_default_secret_key')
DEBUG = config('DEBUG', default=True, cast=bool)

# Detect if running on Heroku
IS_HEROKU = "DYNO" in os.environ

# Spotify API Credentials
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID', default=None)
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET', default=None)

# Debugging environment variables during development
if DEBUG:
    print(f"Running on {'Heroku' if IS_HEROKU else 'Localhost'}")
    print(f"SECRET_KEY: {SECRET_KEY}")
    print(f"DEBUG: {DEBUG}")
    print(f"SPOTIFY_CLIENT_ID: {SPOTIFY_CLIENT_ID}")
    print(f"SPOTIFY_CLIENT_SECRET: {SPOTIFY_CLIENT_SECRET}")

# Allowed Hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.herokuapp.com']

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wrapped.apps.WrappedConfig',  # Your app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'SpotifyWrapped.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'wrapped/templates'],
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

WSGI_APPLICATION = 'SpotifyWrapped.wsgi.application'

# Database Configuration
if IS_HEROKU:
    # Use Heroku database settings
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    # Local SQLite database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For Heroku
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'wrapped/static')]

# Media Files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Activate Django-Heroku
if IS_HEROKU:
    django_heroku.settings(locals())
