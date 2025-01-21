#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_export"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    APP_NAME=app_name,
    BASE_DIR=base_dir,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_navbar.E002", "edc_navbar.E003"],
    EDC_SITES_REGISTER_DEFAULT=True,
    SUBJECT_SCREENING_MODEL="export_app.subjectscreening",
    SUBJECT_CONSENT_MODEL="export_app.subjectconsent",
    SUBJECT_VISIT_MODEL="export_app.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="export_app.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="export_app.subjectrequisition",
    SUBJECT_REFUSAL_MODEL="export_app.subjectrefusal",
    SUBJECT_APP_LABEL="export_app",
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
        "edc_appointment.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "export_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=False,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
