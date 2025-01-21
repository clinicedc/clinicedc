import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_review_dashboard"
base_dir = Path(__file__).parent.parent.parent
print(base_dir)

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_REQUISITION_MODEL="review_dashboard_app.subjectrequisition",
    EDC_NAVBAR_DEFAULT=app_name,
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_navbar.E002", "edc_navbar.E003"],
    EDC_SITES_REGISTER_DEFAULT=True,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_extensions",
        "multisite",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_dashboard.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_listboard.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_model_admin.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_prn.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "review_dashboard_app.apps.EdcFacilityAppConfig",
        "review_dashboard_app.apps.EdcMetadataAppConfig",
        "review_dashboard_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    DASHBOARD_URL_NAMES={},
    DASHBOARD_BASE_TEMPLATES={
        "edc_base_template": "edc_dashboard/base.html",
        "listboard_base_template": "edc_dashboard/base.html",
        "dashboard_base_template": "edc_dashboard/base.html",
        "subject_review_listboard_template": (
            "edc_review_dashboard/subject_review_listboard.html"
        ),
        "subject_dashboard_template": "edc_subject_dashboard/dashboard.html",
    },
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
