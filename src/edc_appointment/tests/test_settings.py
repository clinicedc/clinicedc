import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from edc_test_settings.default_test_settings import DefaultTestSettings

utc = ZoneInfo("UTC")

app_name = "edc_appointment"
base_dir = Path(__file__).absolute().parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    DEBUG=True,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=base_dir / "etc",
    KEY_PATH=base_dir / "etc",
    GIT_DIR=base_dir.parent.parent,
    HOLIDAY_FILE=base_dir / "holidays.csv",
    EDC_RANDOMIZATION_LIST_PATH=base_dir / "etc",
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_sites.E001",
        "edc_navbar.E002",
        "edc_navbar.E003",
    ],
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2016, 10, 2, 0, 0, 0, tzinfo=utc),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2023, 10, 2, 0, 0, 0, tzinfo=utc),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    SUBJECT_SCREENING_MODEL="edc_appointment_app.subjectscreening",
    SUBJECT_CONSENT_MODEL="edc_appointment_app.subjectconsent",
    SUBJECT_VISIT_MODEL="edc_appointment_app.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="edc_appointment_app.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="edc_appointment_app.subjectrequisition",
    SUBJECT_APP_LABEL="edc_appointment_app",
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
        "edc_sites.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_listboard.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_model_admin.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_appointment_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
