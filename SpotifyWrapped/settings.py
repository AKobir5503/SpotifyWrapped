from pathlib import Path
import os
from decouple import config
import django_heroku
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', config('SECRET_KEY')) #config('SECRET_KEY', default='your_default_secret_key')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', config('DEBUG', default=False))
# Retrieve the variables from the environment
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

"""
# Environment variables
SECRET_KEY = config('SECRET_KEY', default='your_default_secret_key')
DEBUG = config('DEBUG', default=False, cast=bool)
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')


print(f"SECRET_KEY: {config('SECRET_KEY', default='MISSING')}")
print(f"DEBUG: {config('DEBUG', default='MISSING', cast=bool)}")
print(f"SPOTIFY_CLIENT_ID: {config('SPOTIFY_CLIENT_ID', default='MISSING')}")
print(f"SPOTIFY_CLIENT_SECRET: {config('SPOTIFY_CLIENT_SECRET', default='MISSING')}")
"""

ALLOWED_HOSTS = ['*']

"""
# Adjust ALLOWED_HOSTS
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['*']
"""

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wrapped.apps.WrappedConfig',
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
ROOT_URLCONF = 'SpotifyWrapped.urls'

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

# Database configuration
IS_HEROKU = "DYNO" in os.environ

if IS_HEROKU:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,  # Persistent connections
            ssl_require=True   # Ensure SSL for PostgreSQL
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # Local SQLite database
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'wrapped/static'),) # test
#STATICFILES_DIRS = []

"""
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'wrapped/static']

if not DEBUG:  # Use this only in production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

django_heroku.settings(locals())

