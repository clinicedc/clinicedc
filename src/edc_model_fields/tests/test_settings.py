#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_model_fields"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "simple_history",
        "django_crypto_fields.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_model_fields.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
