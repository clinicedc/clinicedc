#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_utils"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_sites.E001", "edc_sites.E002"],
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "multisite",
        "edc_auth.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_utils.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    use_test_urls=True,
    add_dashboard_middleware=False,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
