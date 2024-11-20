#!/usr/bin/env python
import sys
from pathlib import Path

from dateutil.relativedelta import relativedelta
from edc_test_settings.default_test_settings import DefaultTestSettings
from edc_utils import get_utcnow

app_name = "edc_adverse_event"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    HOLIDAY_FILE=base_dir / app_name / "tests" / "etc" / "holidays.csv",
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_navbar.E002", "edc_navbar.E003"],
    SUBJECT_VISIT_MODEL="adverse_event_app.subjectvisit",
    ADVERSE_EVENT_APP_LABEL="adverse_event_app",
    ADVERSE_EVENT_ADMIN_SITE="adverse_event_app_admin",
    EMAIL_ENABLED=True,
    EMAIL_CONTACTS={
        "ae_reports": "aereports@example.com",
        "data_manager": "data_manager@example.com",
        "tmg": "tmg@example.com",
    },
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow().replace(
        microsecond=0, second=0, minute=0, hour=0
    )
    - relativedelta(years=2),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow().replace(
        microsecond=999999, second=59, minute=59, hour=11
    )
    + relativedelta(years=2),
    EDC_NAVBAR_DEFAULT=app_name,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
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
        "multisite.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_prn.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
