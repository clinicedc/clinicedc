from django.db import models
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..managers import RequisitionMetadataManager
from .model_mixin import ModelMixin


class RequisitionMetadata(ModelMixin, SiteModelMixin, edc_models.BaseUuidModel):

    panel_name = models.CharField(max_length=50, null=True)

    on_site = CurrentSiteManager()

    objects = RequisitionMetadataManager()

    def __str__(self):
        return (
            f"RequisitionMeta {self.model} {self.visit_schedule_name}."
            f"{self.schedule_name}.{self.visit_code}.{self.visit_code_sequence}@"
            f"{self.timepoint} {self.panel_name} {self.entry_status} "
            f"{self.subject_identifier}"
        )

    @property
    def verbose_name(self):
        from edc_lab.site_labs import site_labs

        return site_labs.panel_names.get(self.panel_name) or self.panel_name

    def natural_key(self):
        return (
            self.panel_name,
            self.model,
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    natural_key.dependencies = ["sites.Site"]

    class Meta(ModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        app_label = "edc_metadata"
        verbose_name = "Requisition Metadata"
        verbose_name_plural = "Requisition Metadata"
        unique_together = (
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "visit_code",
                "visit_code_sequence",
                "model",
                "panel_name",
            ),
        )
        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "timepoint",
                    "model",
                    "entry_status",
                    "show_order",
                    "panel_name",
                ]
            )
        ]
