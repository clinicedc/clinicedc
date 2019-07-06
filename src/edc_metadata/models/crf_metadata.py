from django.apps import apps as django_apps
from django.db import models
from edc_model.models import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from .managers import CrfMetadataManager
from .model_mixin import ModelMixin


class CrfMetadata(ModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = CrfMetadataManager()

    def __str__(self):
        return (
            f"CrfMeta {self.model} {self.visit_code}.{self.visit_code_sequence} "
            f"{self.entry_status} {self.subject_identifier}"
        )

    def natural_key(self):
        return (
            self.model,
            self.subject_identifier,
            self.schedule_name,
            self.visit_schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    natural_key.dependencies = ["sites.Site"]

    @property
    def verbose_name(self):
        model = django_apps.get_model(self.model)
        return model._meta.verbose_name

    class Meta(ModelMixin.Meta):
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"
        unique_together = (
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "visit_code",
                "visit_code_sequence",
                "model",
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
                ]
            )
        ]
