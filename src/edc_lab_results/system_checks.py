from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.checks import Error
from django.core.checks import Warning as CheckWarning


def upload_dir_check(app_configs: object, **kwargs: object) -> list:
    errors: list = []

    upload_dir = getattr(settings, "EDC_LAB_RESULTS_UPLOAD_DIR", None)
    if not upload_dir:
        errors.append(
            CheckWarning(
                "EDC_LAB_RESULTS_UPLOAD_DIR is not set.",
                hint=(
                    "Set EDC_LAB_RESULTS_UPLOAD_DIR in your "
                    "settings to enable lab result uploads."
                ),
                id="edc_lab_results.W001",
            )
        )
        return errors

    base = Path(upload_dir).expanduser()
    if not base.is_dir():
        errors.append(
            Error(
                f"EDC_LAB_RESULTS_UPLOAD_DIR does not exist: {base}",
                hint="Create this directory or update the setting.",
                id="edc_lab_results.E001",
            )
        )
        return errors

    pending = base / "pending"
    processed = base / "processed"

    if not pending.is_dir():
        errors.append(
            Error(
                f"Upload 'pending' directory does not exist: {pending}",
                hint=f"Run: mkdir -p {pending}",
                id="edc_lab_results.E002",
            )
        )

    if not processed.is_dir():
        errors.append(
            Error(
                f"Upload 'processed' directory does not exist: {processed}",
                hint=f"Run: mkdir -p {processed}",
                id="edc_lab_results.E003",
            )
        )

    return errors
