#!/usr/bin/env python
import sys
from pathlib import Path

from edc_constants.constants import DM, HIV, HTN
from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_dx"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=base_dir / app_name / "tests" / "etc",
    SUBJECT_SCREENING_MODEL="edc_metadata.subjectscreening",
    SUBJECT_CONSENT_MODEL="edc_metadata.subjectconsent",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="edc_metadata.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="edc_metadata.subjectrequisition",
    LIST_MODEL_APP_LABEL="edc_dx",
    EDC_SITES_REGISTER_DEFAULT=True,
    REPORT_DATETIME_FIELD_NAME="report_datetime",
    EDC_DX_REVIEW_LIST_MODEL_APP_LABEL="dx_app",
    EDC_DX_REVIEW_APP_LABEL="dx_app",
    EDC_DX_LABELS={
        HIV: HIV,
        DM: "Diabetes",
        HTN: "Hypertension",
    },
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
        "edc_crf.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_dx_review.apps.AppConfig",
        "edc_dx.apps.AppConfig",
        "dx_app.apps.AppConfig",
    ],
    RANDOMIZATION_LIST_PATH=base_dir / app_name / "tests" / "test_randomization_list.csv",
    add_dashboard_middleware=True,
    use_test_urls=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
