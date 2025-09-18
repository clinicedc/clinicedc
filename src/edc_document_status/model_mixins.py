from typing import Any

from django.db import models

from edc_constants.choices import DOCUMENT_STATUS
from edc_constants.constants import COMPLETE


class DocumentStatusModelMixin(models.Model):
    document_status = models.CharField(
        verbose_name="Document status",
        max_length=25,
        choices=DOCUMENT_STATUS,
        default=COMPLETE,
        help_text="If some data is still pending, flag as incomplete",
    )

    document_status_comments = models.TextField(
        verbose_name="Any comments related to status of this document",
        default="",
        blank=True,
        help_text="for example, why some data is still pending",
    )

    def save(self: Any, *args, **kwargs):
        self.update_document_status_on_save(kwargs.get("update_fields"))
        super().save(*args, **kwargs)

    def update_document_status_on_save(self, update_fields: list | None = None) -> None:
        """Updates `document_status` as complete unless field is listed
        in update_fields.

        Used when this instance (subject_visit) needs to be updated.
        For example, after being auto-created and before moving on to CRFs.

        See also: edc_subject_dashboard
        """
        if "document_status" not in (update_fields or []):
            self.document_status = COMPLETE

    class Meta:
        abstract = True
