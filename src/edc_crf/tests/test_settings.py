#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_crf"
base_dir = Path(__file__).parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    GIT_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=[
        "edc_consent.E001",
        "edc_sites.E001",
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
    ],
    SUBJECT_SCREENING_MODEL="edc_crf.subjectscreening",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="edc_visit_tracking.subjectvisitmissed",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.staticfiles",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "multisite",
        "edc_sites.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "visit_tracking_app.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
