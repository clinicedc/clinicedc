from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.files import File

if TYPE_CHECKING:
    from .models import SourceDocument

__all__ = ["archive_source_document", "sha256_of", "source_document_model_cls"]


def source_document_model_cls():
    return django_apps.get_model("edc_lab_results_import.sourcedocument")


def sha256_of(path: Path) -> str:
    """Return the sha256 of the file's bytes, read in chunks.

    Matches the digest `parse_trial_labs` computes while scanning for
    duplicate files, so the same PDF archived from a parsed dataframe
    and from the backfill command collapse onto one `SourceDocument`.
    """
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_source_document(
    path: Path,
    laboratory: str,
    sha256: str | None = None,
) -> tuple[SourceDocument, bool]:
    """Copy `path` into private storage, once per distinct sha256.

    Returns (obj, created). An identical file already archived, under
    this or any other name, is reused rather than copied again. Pass
    `sha256` when the caller already has it, as `ResultImporter` does
    from the `source_file_sha256` column.
    """
    model_cls = source_document_model_cls()
    sha256 = sha256 or sha256_of(path)
    obj = model_cls.objects.filter(sha256=sha256).first()
    if obj:
        return obj, False
    obj = model_cls(
        sha256=sha256,
        filename=path.name,
        laboratory=laboratory,
        file_size=path.stat().st_size,
    )
    with path.open("rb") as f:
        obj.pdf.save(f"{sha256}.pdf", File(f), save=False)
    obj.save()
    return obj, True
