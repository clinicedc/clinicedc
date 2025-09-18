from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel
from edc_sites.managers import CurrentSiteManager

from .. import KEYED, NOT_REQUIRED, REQUIRED
from ..managers import RequisitionMetadataManager
from .crf_metadata_model_mixin import CrfMetadataModelMixin


class RequisitionMetadata(CrfMetadataModelMixin, BaseUuidModel):
    panel_name = models.CharField(max_length=50, default="")

    objects = RequisitionMetadataManager()

    on_site = CurrentSiteManager()

    def __str__(self) -> str:
        return (
            f"RequisitionMeta {self.model} {self.visit_schedule_name}."
            f"{self.schedule_name}.{self.visit_code}.{self.visit_code_sequence}@"
            f"{self.timepoint} {self.panel_name} {self.entry_status} "
            f"{self.subject_identifier}"
        )

    @property
    def verbose_name(self) -> str:
        from edc_lab.site_labs import site_labs  # noqa: PLC0415

        return site_labs.panel_names.get(self.panel_name) or self.panel_name

    def natural_key(self) -> tuple:
        return (
            self.panel_name,
            self.model,
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    # noinspection PyTypeHints
    natural_key.dependencies = ("sites.Site",)  # type: ignore

    def model_instance_query_opts(self) -> dict:
        opts = super().model_instance_query_opts()
        opts.update(panel__name=self.panel_name)
        return opts

    def refresh_entry_status(self) -> str:
        """Resets entry_status to the original visit schedule value"""
        if not self.model_instance:
            if self.visit_code_sequence > 0:
                self.entry_status = REQUIRED
            else:
                visit = self.visits.get(self.visit_code)
                for required in [
                    req.required
                    for req in visit.requisitions
                    if req.model == self.model and req.panel.name == self.panel_name
                ]:
                    self.entry_status = REQUIRED if required else NOT_REQUIRED
        else:
            self.entry_status = KEYED
        self.save_base(update_fields=["entry_status"])
        return self.entry_status

    class Meta(CrfMetadataModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "edc_metadata"
        verbose_name = "Requisition collection status"
        verbose_name_plural = "Requisition collection status"
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
                name="%(app_label)s_%(class)s_subject_iden_visit_uniq",
            ),
        )
        indexes = (
            *CrfMetadataModelMixin.Meta.indexes,
            *BaseUuidModel.Meta.indexes,
            models.Index(
                fields=[
                    "site",
                    "entry_status",
                    "visit_code",
                    "visit_code_sequence",
                    "model",
                    "panel_name",
                    "subject_identifier",
                    "schedule_name",
                    "visit_schedule_name",
                ],
            ),
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "model",
                    "panel_name",
                    "entry_status",
                    "timepoint",
                    "show_order",
                ],
            ),
        )
