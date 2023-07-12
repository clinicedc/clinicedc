from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.db import models

from ...constants import CRF, NOT_REQUIRED, REQUIRED
from ...metadata_updater import MetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin as Base

    from ...models import CrfMetadata
    from ..creates import CreatesMetadataModelMixin
    from .updates_crf_metadata_model_mixin import UpdatesCrfMetadataModelMixin

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass

    class CrfModel(UpdatesCrfMetadataModelMixin, Base):
        related_visit = models.ForeignKey(RelatedVisitModel, on_delete=models.PROTECT)


class UpdatesCrfMetadataModelMixin(UpdatesMetadataModelMixin):
    """A model mixin used on CRF models to enable them to
    update `metadata` upon save and delete.
    """

    metadata_updater_cls: MetadataUpdater = MetadataUpdater
    metadata_category: str = CRF

    @property
    def metadata_updater(self: CrfModel) -> MetadataUpdater:
        """Returns an instance of MetadataUpdater."""
        return self.metadata_updater_cls(
            related_visit=self.related_visit,
            target_model=self._meta.label_lower,
            allow_create=True,
        )

    @property
    def metadata_query_options(self: CrfModel) -> dict:
        return super().metadata_query_options

    @property
    def metadata_model(self: CrfModel) -> Type[CrfMetadata]:
        """Returns the metadata model associated with self."""
        metadata_model = "edc_metadata.crfmetadata"
        return django_apps.get_model(metadata_model)

    @property
    def metadata_default_entry_status(self: CrfModel) -> str:
        """Returns a string that represents the default entry status
        of the CRF in the visit schedule.
        """
        crfs_prn = self.metadata_visit_object.crfs_prn
        if self.related_visit.visit_code_sequence != 0:
            crfs = self.metadata_visit_object.crfs_unscheduled + crfs_prn
        else:
            crfs = self.metadata_visit_object.crfs + crfs_prn
        crf = [c for c in crfs if c.model == self._meta.label_lower][0]
        return REQUIRED if crf.required else NOT_REQUIRED

    class Meta:
        abstract = True
