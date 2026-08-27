from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.checks import Error
from django.core.checks import Warning as CheckWarning

from edc_lab_results_import.utils import private_path_attr


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
                id="edc_lab_results_import.W001",
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
                id="edc_lab_results_import.E002",
            )
        )

    if not processed.is_dir():
        errors.append(
            Error(
                f"Upload 'processed' directory does not exist: {processed}",
                hint=f"Run: mkdir -p {processed}",
                id="edc_lab_results_import.E003",
            )
        )

    return errors


def private_path_check(app_configs: object, **kwargs: object) -> list:
    errors: list = []
    private_path: str = getattr(settings, private_path_attr, "")
    if not private_path:
        errors.append(
            Error(
                f"{private_path_attr} is not set.",
                hint=(
                    f"Set {private_path_attr} to the folder where original "
                    "result PDFs are archived."
                ),
                id="edc_lab_results_import.E004",
            )
        )
        return errors

    base = Path(private_path).expanduser()
    if not base.is_dir():
        errors.append(
            Error(
                f"{private_path_attr} does not exist: {base}",
                hint=f"Run: mkdir -p {base}",
                id="edc_lab_results_import.E005",
            )
        )
    return errors
