from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from edc_model.models import BaseUuidModel

from ..choices import STATUS_CHOICES
from ..constants import PENDING


class UploadedResultFile(BaseUuidModel):
    original_filename = models.CharField(
        max_length=255,
        help_text="Original filename as uploaded by the clinician.",
    )

    stored_filename = models.CharField(
        max_length=255,
        unique=True,
        help_text="UUID-based filename on disk.",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True,
    )

    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error details if import failed.",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    uploaded_datetime = models.DateTimeField(auto_now_add=True)

    imported_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.status})"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Uploaded Result File"
        verbose_name_plural = "Uploaded Result Files"
        ordering: ClassVar = ["-uploaded_datetime"]
