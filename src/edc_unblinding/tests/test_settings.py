#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_unblinding"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    template_dirs=[base_dir / app_name / "tests" / "templates"],
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=base_dir / app_name / "tests" / "etc",
    EDC_AUTH_CODENAMES_WARN_ONLY=True,
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_consent.E001",
        "edc_sites.E001",
    ],
    SUBJECT_SCREENING_MODEL="visit_schedule_app.subjectscreening",
    SUBJECT_CONSENT_MODEL="visit_schedule_app.subjectconsent",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="visit_schedule_app.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="visit_schedule_app.subjectrequisition",
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
        "edc_action_item.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_label.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_prn.apps.AppConfig",
        "edc_pdf_reports.apps.AppConfig",
        "edc_unblinding.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "visit_tracking_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    DASHBOARD_BASE_TEMPLATES={
        "dashboard_template": (
            base_dir / "edc_unblinding" / "tests" / "templates" / "dashboard.html"
        ),
        "dashboard2_template": (
            base_dir / "edc_unblinding" / "tests" / "templates" / "dashboard2.html"
        ),
    },
    use_test_urls=True,
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
).settings
for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
