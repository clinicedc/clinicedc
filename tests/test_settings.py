#!/usr/bin/env python
import sys
from pathlib import Path

from dateutil.relativedelta import relativedelta
from edc_test_settings.default_test_settings import DefaultTestSettings

from edc_utils import get_utcnow

app_name = "edc_pharmacy"
base_dir = Path(__file__).absolute().parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    use_test_urls=True,
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_action_item.W001",
    ],
    DJANGO_REVISION_IGNORE_WORKING_DIR=True,
    EDC_AUTH_CODENAMES_WARN_ONLY=True,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    EDC_SITES_REGISTER_DEFAULT=True,
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=(
        get_utcnow().replace(microsecond=0, second=0, minute=0, hour=0)
        - relativedelta(years=6)
    ),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=(
        get_utcnow().replace(microsecond=999999, second=59, minute=59, hour=11)
        + relativedelta(years=6)
    ),
    SUBJECT_SCREENING_MODEL="edc_screening.subjectscreening",
    SUBJECT_CONSENT_MODEL="edc_consent.subjectconsent",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="edc_visit_tracking.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="edc_lab.subjectrequisition",
    SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal",
    # SUBJECT_APP_LABEL=f"{self.app_name}",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.staticfiles",
        "django_crypto_fields.apps.AppConfig",
        "django_pylabels.apps.AppConfig",
        "multisite",
        "sequences.apps.SequencesConfig",
        "fontawesomefree",
        "logentry_admin",
        "rangefilter",
        "simple_history",
        "storages",
        "django_db_views",
        "django_extensions",
        "django_crypto_fields.apps.AppConfig",
        "django_pylabels.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adherence.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_dashboard.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_model_admin.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_pdutils.apps.AppConfig",
        "edc_pharmacy.apps.AppConfig",
        "edc_pylabels.apps.AppConfig",
        "edc_qareports.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_visit_schedule_app.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "data_manager_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
