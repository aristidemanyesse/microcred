"""
Django settings for Microcred.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

_allowed = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = ['https://www.assana-services.com', "https://test.assana-services.com"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    "AuthentificationApp",
    "FinanceApp",
    "FidelisApp",
    "TresorApp",
    "MainApp",
    "StatsApp",
    "CoreApp",
    
    "django_crontab",
    "mathfilters"
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

ROOT_URLCONF = 'settings.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'HOST'    : os.getenv('DB_HOST'),
        'PORT'    : os.getenv('DB_PORT', '3306'),
        'USER'    : os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'NAME'    : os.getenv('DB_NAME'),
    },
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

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT      = True
    SESSION_COOKIE_SECURE    = True
    CSRF_COOKIE_SECURE       = True
    SECURE_HSTS_SECONDS      = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

AUTH_USER_MODEL = 'AuthentificationApp.Employe'
LOGIN_URL = 'AuthentificationApp:login'
LOGIN_REDIRECT_URL = 'MainApp:dashboard'
LOGOUT_REDIRECT_URL = 'AuthentificationApp:logout'

USE_THOUSAND_SEPARATOR = True

CRONTAB_DJANGO_PROJECT_NAME = "Microcred"
CRONJOBS = [
    # chaque jour à minuit → calcul pénalités
    ('0 0 * * *', 'FinanceApp.crons.generer_penalites', '>> {}'.format(os.path.join(BASE_DIR, "logs/penelites.log" ))),

    # # chaque jour à 01h → calcul intérêts épargne
    ('0 1 * * *', 'FinanceApp.crons.generer_interets_epargnes', '>> {}'.format(os.path.join(BASE_DIR, "logs/interets.log" ))),
    
    
    # ('* * * * *', 'FinanceApp.crons.generer_penalites', '>> {}'.format(os.path.join(BASE_DIR, "logs/penelites.txt" ))),
    # ('* * * * *', 'FinanceApp.crons.generer_interets_epargnes', '>> {}'.format(os.path.join(BASE_DIR, "logs/interets.txt" ))),
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'FinanceApp': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'FidelisApp': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'MainApp':    {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'TresorApp':  {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'CoreApp':    {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'AuthentificationApp': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

# mariadb-dump -u root -p microcred > backup_file.sql
# mariadb -u root -p microcred_dev < backup_file.sql
