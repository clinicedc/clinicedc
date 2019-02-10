import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "edc_consent"
SITE_ID = 40

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "7vm9v5faf9tf6h9ck#&yb4d&$9p!wxr__7y8&p!6a-a3=l-6sd"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "simple_history",
    "django_crypto_fields.apps.AppConfig",
    "django_revision.apps.AppConfig",
    "edc_appointment.apps.AppConfig",
    "edc_base.apps.AppConfig",
    "edc_timepoint.apps.AppConfig",
    "edc_device.apps.AppConfig",
    "edc_identifier.apps.AppConfig",
    "edc_action_item.apps.AppConfig",
    "edc_locator.apps.AppConfig",
    "edc_metadata.apps.AppConfig",
    "edc_notification.apps.AppConfig",
    "edc_registration.apps.AppConfig",
    "edc_visit_schedule.apps.AppConfig",
    "edc_visit_tracking.apps.AppConfig",
    "edc_consent.apps.EdcProtocolAppConfig",
    "edc_consent.apps.AppConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "edc_dashboard.middleware.DashboardMiddleware",
    "edc_subject_dashboard.middleware.DashboardMiddleware",
]

ROOT_URLCONF = "edc_consent.urls"

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
            ]
        },
    }
]

WSGI_APPLICATION = "edc_consent.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

DASHBOARD_URL_NAMES = {
    "subject_listboard_url": "edc_subject_dashboard:subject_listboard_url",
    "subject_dashboard_url": "edc_subject_dashboard:subject_dashboard_url",
}

EDC_BOOTSTRAP = 3
EMAIL_ENABLED = False
EMAIL_CONTACTS = {}

if "test" in sys.argv:

    class DisableMigrations:
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
    DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
