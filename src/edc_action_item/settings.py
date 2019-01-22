import environ
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETC_DIR = BASE_DIR
LIVE_SYSTEM = False
# AUTO_CREATE_KEYS = True

# to enable a test that actually sends notifications
# $ export ENVFILE=.env
# $ echo $ENVFILE
# .env
env = environ.Env(
    DJANGO_EDC_BOOTSTRAP=(int, 3),
    DJANGO_EMAIL_ENABLED=(bool, False),
    TWILIO_ENABLED=(bool, False),
)

try:
    ENVFILE = os.environ["ENVFILE"] or "env.sample"
except KeyError:
    ENVFILE = "env.sample"
env.read_env(os.path.join(BASE_DIR, ENVFILE))
print(f"Reading env from {os.path.join(BASE_DIR, ENVFILE)}")


APP_NAME = "edc_action_item"
SITE_ID = 40

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "40murs6#^^rlu&jv+_)px#9pb&1f&upm1q$e9je#8tdl4mtq)^"

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
    "django_crypto_fields.apps.AppConfig",
    "django_revision.apps.AppConfig",
    "django_collect_offline.apps.AppConfig",
    "django_collect_offline_files.apps.AppConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "simple_history",
    "edc_auth.apps.AppConfig",
    "edc_base.apps.AppConfig",
    "edc_protocol.apps.AppConfig",
    "edc_identifier.apps.AppConfig",
    "edc_device.apps.AppConfig",
    "edc_notification.apps.AppConfig",
    "edc_visit_schedule.apps.AppConfig",
    "edc_action_item.apps.AppConfig",
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

ROOT_URLCONF = "edc_action_item.urls"

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

WSGI_APPLICATION = "edc_action_item.wsgi.application"


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'edc',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = "/static/"


DASHBOARD_URL_NAMES = {"subject_dashboard_url": "edc_action_item:subject_dashboard_url"}

EDC_BOOTSTRAP = 3
DJANGO_COLLECT_OFFLINE_FILES_USER = None
DJANGO_COLLECT_OFFLINE_FILES_REMOTE_HOST = None
DJANGO_COLLECT_OFFLINE_FILES_USB_VOLUME = None

EMAIL_ENABLED = env("DJANGO_EMAIL_ENABLED")
if EMAIL_ENABLED:
    EMAIL_HOST = env.str("DJANGO_EMAIL_HOST")
    EMAIL_PORT = env.int("DJANGO_EMAIL_PORT")
    EMAIL_HOST_USER = env.str("DJANGO_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env.str("DJANGO_EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env("DJANGO_EMAIL_USE_TLS")
    MAILGUN_API_KEY = env("MAILGUN_API_KEY")
    MAILGUN_API_URL = env("MAILGUN_API_URL")
EMAIL_CONTACTS = {"data_manager": "data_manager@clinicedc.org"}
# if ENVFILE != '.env':
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TWILIO_ENABLED = env("TWILIO_ENABLED")
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN")
TWILIO_SENDER = env.str("TWILIO_SENDER")
TWILIO_TEST_RECIPIENT = env.str("TWILIO_TEST_RECIPIENT")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        }
    },
}


if "test" in sys.argv:

    class DisableMigrations:
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
    DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
