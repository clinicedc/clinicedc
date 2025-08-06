#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_view_utils"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / "edc_view_utils" / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_sites.E001",
        "edc_sites.E002",
    ],
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    EDC_SITES_REGISTER_DEFAULT=False,
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
    ROOT_URLCONF="dashboard_app.urls",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_extensions",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "multisite",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_dashboard.apps.AppConfig",
        "edc_label.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_listboard.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_model_admin.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "dashboard_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
