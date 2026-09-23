from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.checks import Error

from .utils import storage_dir_attr, upload_dir_attr


def _dir_errors(attr: str, hint: str, not_set_id: str, not_found_id: str) -> list:
    """Return errors for a folder setting that is not set or does
    not exist.

    Reads settings directly rather than calling the getters in
    `utils`, which raise instead of reporting.
    """
    location = getattr(settings, attr, None)
    if not location:
        return [Error(f"{attr} is not set.", hint=hint, id=not_set_id)]
    base = Path(location).expanduser()
    if not base.is_dir():
        return [
            Error(
                f"{attr} does not exist or is not a folder: {base}",
                hint=f"Run: mkdir -p {base}",
                id=not_found_id,
            )
        ]
    return []


def storage_dir_check(app_configs: object, **kwargs: object) -> list:
    return _dir_errors(
        storage_dir_attr,
        hint=(
            f"Set {storage_dir_attr} to the folder where original result PDFs "
            "are archived after import."
        ),
        not_set_id="edc_lab_results_import.E004",
        not_found_id="edc_lab_results_import.E005",
    )


def upload_dir_check(app_configs: object, **kwargs: object) -> list:
    return _dir_errors(
        upload_dir_attr,
        hint=(
            f"Set {upload_dir_attr} to the folder where result PDFs are uploaded for import."
        ),
        not_set_id="edc_lab_results_import.E006",
        not_found_id="edc_lab_results_import.E007",
    )


def upload_and_storage_dirs_check(app_configs: object, **kwargs: object) -> list:
    """Return an error if the upload folder is the storage folder or
    is inside it.

    Archived copies are content-addressed and managed by
    `SourceDocument`. Uploaded PDFs must not be mixed in with them.
    """
    storage_dir = getattr(settings, storage_dir_attr, None)
    upload_dir = getattr(settings, upload_dir_attr, None)
    if not storage_dir or not upload_dir:
        return []
    storage_dir = Path(storage_dir).expanduser().resolve()
    upload_dir = Path(upload_dir).expanduser().resolve()
    if upload_dir == storage_dir or upload_dir.is_relative_to(storage_dir):
        return [
            Error(
                f"{upload_dir_attr} may not be the same as or inside "
                f"{storage_dir_attr}. Got {upload_dir}.",
                hint=(
                    "Use a separate folder for uploads. The storage folder is "
                    "managed by the application."
                ),
                id="edc_lab_results_import.E008",
            )
        ]
    return []
