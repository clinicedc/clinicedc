from __future__ import annotations

from django.db import models
from django.db.models import UniqueConstraint

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords

from .metadata_unavailable_model_mixin import MetadataUnavailableModelMixin


class RequisitionMetadataUnavailable(MetadataUnavailableModelMixin, BaseUuidModel):
    """Flags an outstanding (REQUIRED) requisition as data unavailable. Keyed by
    the requisition natural key, which includes ``panel_name``."""

    panel_name = models.CharField(max_length=50, default="")

    history = HistoricalRecords()

    def __str__(self) -> str:
        return (
            f"{self.model} {self.panel_name} {self.visit_code}."
            f"{self.visit_code_sequence} {self.subject_identifier}"
        )

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        verbose_name = "Requisition data unavailable"
        verbose_name_plural = "Requisition data unavailable"
        constraints = (
            UniqueConstraint(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "model",
                    "panel_name",
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
                name="edc_md_requnavail_a0idx",
            ),
        )
