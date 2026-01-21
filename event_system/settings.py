from pathlib import Path

try:
    import dj_database_url
except ModuleNotFoundError:  # allows running locally without this dependency installed
    dj_database_url = None
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-assignment-key'

DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com', 'http://127.0.0.1:8000']

INSTALLED_APPS = [
    'django.contrib.admin',      
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'events',   
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

ROOT_URLCONF = 'event_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'event_system.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

if dj_database_url:
    DATABASES = {
        'default': dj_database_url.config(
            # Replace this value with your local database's connection string.
            default='postgresql://event_management_db_ay71_user:hGMLD2NMaqf64GYyDofUSL4iTRDc7oeP@dpg-d5igl85actks73a55r8g-a.oregon-postgres.render.com/event_management_db_ay71',
            conn_max_age=600
        )
    }
else:
    # Fallback for local/dev if dj-database-url isn't installed
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Site URL for activation links
SITE_URL = 'http://127.0.0.1:8000/'

# Authentication settings
LOGIN_REDIRECT_URL = 'login_redirect'
LOGOUT_REDIRECT_URL = 'event_list'
LOGIN_URL = 'login'

# Email settings
if DEBUG:
    # Use console backend for development - emails will be printed to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Use SMTP backend for production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your email
    EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your app password

DEFAULT_FROM_EMAIL = 'noreply@eventmanagement.com'