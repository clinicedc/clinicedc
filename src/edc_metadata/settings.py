import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = 'edc_metadata'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ztj1y9k+4m@k(cut_mx6k&x&_*)-g0e#nfz=9)-#296j3*hbrq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crypto_fields.apps.AppConfig',
    'django_revision.apps.AppConfig',
    'edc_base.apps.AppConfig',
    'edc_sync.apps.AppConfig',
    'edc_appointment.apps.AppConfig',
    'edc_offstudy.apps.AppConfig',
    'edc_timepoint.apps.AppConfig',
    'edc_device.apps.AppConfig',
    'edc_protocol.apps.AppConfig',
    'edc_registration.apps.AppConfig',
    'edc_visit_schedule.apps.AppConfig',
    'edc_identifier.apps.AppConfig',
    'edc_metadata.apps.EdcVisitTrackingAppConfig',
    'edc_metadata.apps.AppConfig',
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

ROOT_URLCONF = 'edc_metadata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'edc_metadata.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
GIT_DIR = BASE_DIR
KEY_PATH = os.path.join(BASE_DIR, 'crypto_fields')

if 'test' in sys.argv:
    MIGRATION_MODULES = {
        "django_crypto_fields": None,
        "edc_appointment": None,
        "edc_consent": None,
        "edc_identifier": None,
        "edc_metadata": None,
        "edc_registration": None,
        "edc_sync": None,
        "edc_offstudy": None,
        'admin': None,
        "auth": None,
        'contenttypes': None,
        'sessions': None,
    }
if 'test' in sys.argv:
    PASSWORD_HASHERS = ('django_plainpasswordhasher.PlainPasswordHasher', )
if 'test' in sys.argv:
    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
