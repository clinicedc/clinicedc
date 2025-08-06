#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_form_label"

base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_navbar.E002", "edc_navbar.E003"],
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="visit_schedule_app.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="visit_schedule_app.subjectrequisition",
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
        "edc_auth.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_search.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_form_label.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
