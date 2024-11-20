"""
Here only so we can run makemessages

"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+#-*m&byi1w8=#e5nr))^kollb=k1b#rvjffo#+teji^qpm14o"  # nosec B105

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DJANGO_CRYPTO_FIELDS_KEY_PATH = BASE_DIR / ".etc"
AUTO_CREATE_KEYS = True
APP_NAME = "edc_pharmacy"

SUBJECT_VISIT_MODEL = "edc_visit_tracking.subjectvisit"
EDC_PROTOCOL_STUDY_OPEN_DATETIME = datetime(2013, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))
EDC_PROTOCOL_STUDY_CLOSE_DATETIME = datetime(2033, 10, 15, tzinfo=ZoneInfo("Africa/Gaborone"))
EDC_ADVERSE_EVENT_APP_LABEL = "edc_adverse_event"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_crypto_fields.apps.AppConfig",
    "django_pylabels.apps.AppConfig",
    "edc_pylabels.apps.AppConfig",
    "edc_sites.apps.AppConfig",
    "edc_notification.apps.AppConfig",
    "edc_action_item.apps.AppConfig",
    "edc_registration.apps.AppConfig",
    "edc_visit_schedule.apps.AppConfig",
    "edc_visit_tracking.apps.AppConfig",
    "edc_appointment.apps.AppConfig",
    "edc_pharmacy.apps.AppConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "edc_model_admin.context_processors.admin_theme",
                "edc_constants.context_processor.constants",
                "edc_appointment.context_processors.constants",
                "edc_visit_tracking.context_processors.constants",
            ]
        },
    }
]

ROOT_URLCONF = "edc_pharmacy.urls"


WSGI_APPLICATION = "edc_pharmacy.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
