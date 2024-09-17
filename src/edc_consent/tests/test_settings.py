#!/usr/bin/env python
import sys
from pathlib import Path

from dateutil.relativedelta import relativedelta
from edc_test_settings.default_test_settings import DefaultTestSettings
from edc_utils import get_utcnow

app_name = "edc_consent"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SILENCED_SYSTEM_CHECKS=[
        "edc_consent.E001",
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_sites.E001",
    ],
    EDC_NAVBAR_DEFAULT="edc_consent",
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=1),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    SUBJECT_SCREENING_MODEL="consent_app.subjectscreening",
    SUBJECT_CONSENT_MODEL="consent_app.subjectconsent",
    SUBJECT_VISIT_MODEL="consent_app.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="consent_app.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="consent_app.subjectrequisition",
    SUBJECT_REFUSAL_MODEL="consent_app.subjectrefusal",
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
        "django_revision.apps.AppConfig",
        "multisite",
        "adverse_event_app.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "consent_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
