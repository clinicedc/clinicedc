#!/usr/bin/env python
import sys
from pathlib import Path

from dateutil.relativedelta import relativedelta
from edc_test_settings.default_test_settings import DefaultTestSettings
from edc_utils import get_utcnow

app_name = "edc_adherence"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    LIST_MODEL_APP_LABEL="edc_adherence",
    EDC_SITES_REGISTER_DEFAULT=True,
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=(
        get_utcnow().replace(microsecond=0, second=0, minute=0, hour=0)
        - relativedelta(years=6)
    ),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=(
        get_utcnow().replace(microsecond=999999, second=59, minute=59, hour=11)
        + relativedelta(years=6)
    ),
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
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_model_admin.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_adherence.apps.AppConfig",
    ],
    RANDOMIZATION_LIST_PATH=str(base_dir / app_name / "tests" / "test_randomization_list.csv"),
    add_dashboard_middleware=False,
    use_test_urls=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
