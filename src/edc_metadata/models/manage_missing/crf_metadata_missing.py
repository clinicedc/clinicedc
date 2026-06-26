from __future__ import annotations

from django.db import models
from django.db.models import UniqueConstraint

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords

from .model_mixins import ManageMissingModelMixin


class CrfMetadataMissing(ManageMissingModelMixin, BaseUuidModel):
    """Flags an outstanding (REQUIRED) CRF as data unavailable so the review
    screen stops counting it. Reversible (delete the row); the history table
    retains the audit trail."""

    history = HistoricalRecords()

    def __str__(self) -> str:
        return (
            f"{self.model} {self.visit_code}.{self.visit_code_sequence} "
            f"{self.subject_identifier}"
        )

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        verbose_name = "CRF flagged missing"
        verbose_name_plural = "CRFs flagged missing"
        constraints = (
            UniqueConstraint(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "model",
                ],
                name="%(app_label)s_%(class)s_natkey_uniq",
            ),
        )
        indexes = (
            *BaseUuidModel.Meta.indexes,
            *NonUniqueSubjectIdentifierFieldMixin.Meta.indexes,
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                ],
                # short name to stay within Django's 30-char index-name limit
                name="edc_md_crfunavail_a0idx",
            ),
        )
