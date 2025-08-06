#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_model"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    APP_NAME="edc_model",
    BASE_DIR=base_dir,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    KEY_PATH=str(base_dir / app_name / "tests" / "etc"),
    ALLOWED_HOSTS=["localhost"],
    ROOT_URLCONF=f"{app_name}.tests.urls",
    STATIC_URL="/static/",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "multisite",
        "django_crypto_fields.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_model.apps.AppConfig",
    ],
    add_dashboard_middleware=False,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
