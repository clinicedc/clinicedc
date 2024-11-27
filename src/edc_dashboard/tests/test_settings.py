#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_auth"
base_dir = Path(__file__).absolute().parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    DJANGO_CRYPTO_FIELDS_KEY_PATH=base_dir / "tests" / "etc",
    SILENCED_SYSTEM_CHECKS=[
        "edc_sites.E001",
        "edc_sites.E002",
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
    ],
    EDC_AUTH_CODENAMES_WARN_ONLY=True,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
