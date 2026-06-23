from __future__ import annotations

from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel

from ..choices import METADATA_KIND, PRIORITY_TIER
from ..constants import CRF


class CrfPriority(BaseUuidModel):
    """A data-manager maintained priority for a CRF (or requisition) type
    within a schedule.

    Drives the default form set and tier highlighting on the metadata
    review screen so teams can focus follow-up on the forms that matter
    most when resources are limited.

    Note: requisition prioritisation is keyed on the requisition `model`
    label only; panel-level prioritisation is deferred.
    """

    model = models.CharField(
        max_length=50,
        help_text="Dotted model label, e.g. 'my_app.myform'. Matches CrfMetadata.model.",
    )

    visit_schedule_name = models.CharField(max_length=25)

    schedule_name = models.CharField(max_length=25)

    metadata_kind = models.CharField(max_length=25, choices=METADATA_KIND, default=CRF)

    tier = models.IntegerField(
        choices=PRIORITY_TIER,
        default=2,
        help_text="Lower is higher priority. Tier 1 is highlighted on the review screen.",
    )

    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.model} ({self.schedule_name}) tier {self.tier}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "CRF priority"
        verbose_name_plural = "CRF priorities"
        ordering = ("tier", "schedule_name", "model")
        constraints = (
            UniqueConstraint(
                fields=["model", "visit_schedule_name", "schedule_name", "metadata_kind"],
                name="%(app_label)s_%(class)s_model_schedule_uniq",
            ),
        )
        indexes = (
            *BaseUuidModel.Meta.indexes,
            models.Index(
                fields=["active", "schedule_name", "tier"],
                name="%(app_label)s_%(class)s_a0idx",
            ),
        )
