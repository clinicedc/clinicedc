#!/usr/bin/env python
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from edc_test_utils import DefaultTestSettings

app_name = "edc_visit_tracking"


base_dir = Path(__file__).parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SITE_ID=1,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_consent.E001",
    ],
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    EDC_LTFU_MODEL_NAME="edc_ltfu.ltfu",
    EDC_SITES_REGISTER_DEFAULT=True,
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(
        year=2017, month=1, day=1, tzinfo=ZoneInfo("UTC")
    ),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(
        year=2021, month=1, day=1, tzinfo=ZoneInfo("UTC")
    ),
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
        "edc_action_item.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
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
        "visit_tracking_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
