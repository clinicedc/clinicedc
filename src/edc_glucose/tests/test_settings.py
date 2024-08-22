#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_glucose"

base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    LIST_MODEL_APP_LABEL="edc_glucose",
    SILENCED_SYSTEM_CHECKS=["sites.E101", "edc_navbar.E002", "edc_navbar.E003"],
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    EXTRA_INSTALLED_APPS=[
        "edc_glucose.apps.AppConfig",
        "edc_dx.apps.AppConfig",
        "edc_dx_review.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
    ],
    EDC_DX_LABELS=dict(dm="Diabetes"),
    EDC_DX_REVIEW_LIST_MODEL_APP_LABEL="edc_glucose",
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
    use_test_urls=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
