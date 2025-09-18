from django.apps import apps as django_apps
from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel

from ..managers import CrfMetadataManager
from .crf_metadata_model_mixin import CrfMetadataModelMixin


class CrfMetadata(CrfMetadataModelMixin, BaseUuidModel):
    objects = CrfMetadataManager()

    def __str__(self) -> str:
        return (
            f"CrfMeta {self.model} {self.visit_schedule_name}.{self.schedule_name}."
            f"{self.visit_code}.{self.visit_code_sequence}@{self.timepoint} "
            f"{self.entry_status} {self.subject_identifier}"
        )

    def natural_key(self) -> tuple:
        return (
            self.model,
            self.subject_identifier,
            self.schedule_name,
            self.visit_schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    # noinspection PyTypeHints
    natural_key.dependencies = ("sites.Site",)

    @property
    def verbose_name(self) -> str:
        try:
            model = django_apps.get_model(self.model)
        except LookupError as e:
            return f"{e}. You need to regenerate metadata."
        return model._meta.verbose_name

    class Meta(CrfMetadataModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Crf collection status"
        verbose_name_plural = "Crf collection status"
        unique_together = ()
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
                    "entry_status",
                    "timepoint",
                    "show_order",
                ],
            ),
        )
