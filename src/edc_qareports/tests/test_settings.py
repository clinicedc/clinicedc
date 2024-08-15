#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_qareports"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_consent.E001",
    ],
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    EDC_SITES_REGISTER_DEFAULT=True,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "multisite",
        "django_db_views",
        "edc_auth.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_qareports.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=False,
    add_lab_dashboard_middleware=False,
    add_adverse_event_dashboard_middleware=False,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
