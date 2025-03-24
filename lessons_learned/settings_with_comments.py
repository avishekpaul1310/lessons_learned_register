"""
Django settings for lessons_learned project.

This file contains all the configuration settings for the Lessons Learned System.
It includes settings for database connections, static/media files, installed apps,
authentication, and other Django-specific configurations.

For production deployment, several settings should be modified:
1. Set DEBUG to False
2. Update ALLOWED_HOSTS with your domain
3. Configure a production-ready database (PostgreSQL recommended)
4. Set up a proper email backend
5. Configure static and media file hosting

Environment variables can be used to override these settings for different environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this should be set as an environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-7!9ah2bymdpk))4#uy8*%=!j5&n+xz+fru$w7@*si(d(8a7143')

# SECURITY WARNING: don't run with debug turned on in production!
# Should be set to False in production
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Add your domain to ALLOWED_HOSTS in production
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
# List of all Django apps used in the project
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',            # Admin interface
    'django.contrib.auth',             # Authentication system
    'django.contrib.contenttypes',     # Content type framework
    'django.contrib.sessions',         # Session framework
    'django.contrib.messages',         # Messaging framework
    'django.contrib.staticfiles',      # Static files management
    
    # Third-party apps
    'crispy_forms',                    # Better form rendering
    'crispy_bootstrap4',               # Bootstrap 4 template pack for crispy forms
    'django_filters',                  # Advanced filtering
    'django_summernote',               # Rich text editor
    
    # Project apps
    'accounts.apps.AccountsConfig',    # User accounts and profiles
    'projects.apps.ProjectsConfig',    # Project management
    'lessons.apps.LessonsConfig',      # Lessons learned core functionality
]

# Middleware configuration
# These are executed in order for each request/response cycle
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware',    # Session support
    'django.middleware.common.CommonMiddleware',               # Common features
    'django.middleware.csrf.CsrfViewMiddleware',               # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentication
    'django.contrib.messages.middleware.MessageMiddleware',    # Messaging
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]

# Root URL configuration
ROOT_URLCONF = 'lessons_learned.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Template engine
        'DIRS': [os.path.join(BASE_DIR, 'templates')],                 # Project-level template directories
        'APP_DIRS': True,                                              # Look for templates in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',            # Adds debug variables
                'django.template.context_processors.request',          # Adds request object
                'django.contrib.auth.context_processors.auth',         # Adds user authentication
                'django.contrib.messages.context_processors.messages', # Adds messaging
            ],
        },
    },
]

# WSGI application for deployment
WSGI_APPLICATION = 'lessons_learned.wsgi.application'

# Database configuration
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Default uses SQLite, but PostgreSQL is recommended for production
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en-us'    # Default language
TIME_ZONE = 'UTC'          # Time zone setting
USE_I18N = True            # Internationalization
USE_TZ = True              # Time zone support

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# URL prefix for static files
STATIC_URL = 'static/'

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Directory where collectstatic will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'  # Use Bootstrap 4 for form rendering

# Authentication settings
LOGIN_REDIRECT_URL = 'dashboard'  # Where to redirect after login
LOGIN_URL = 'login'              # URL for the login page

# Email settings
# In development, emails are printed to the console
# In production, configure a real email backend
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 
    'django.core.mail.backends.console.EmailBackend'
)

# SMTP settings for production (used if EMAIL_BACKEND is smtp)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@lessonslearned.example.com')

# Site URL for links in emails
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Summernote configuration
SUMMERNOTE_CONFIG = {
    'summernote': {
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
        'width': '100%',
        'height': '300px',
    },
    'attachment_upload_to': 'summernote_uploads/',
}

# Security settings for production
if not DEBUG:
    # HTTPS settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
