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
        "edc_sites.E001",
        "edc_sites.E002",
    ],
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    EDC_SITES_REGISTER_DEFAULT=False,
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
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_panel.apps.AppConfig",
        "edc_lab_results.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_qareports.apps.AppConfig",
        "edc_appointment_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=False,
    add_adverse_event_dashboard_middleware=False,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
