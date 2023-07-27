from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.db import models

from ...constants import NOT_REQUIRED, REQUIRED, REQUISITION
from ...requisition import RequisitionMetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin as Base
    from edc_lab.models import Panel

    from ...models import RequisitionMetadata
    from ..creates import CreatesMetadataModelMixin
    from .updates_requisition_metadata_model_mixin import (
        UpdatesRequisitionMetadataModelMixin,
    )

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass

    class RequisitionModel(UpdatesRequisitionMetadataModelMixin, Base):
        related_visit = models.ForeignKey(RelatedVisitModel, on_delete=models.PROTECT)
        panel = models.ForeignKey(Panel, on_delete=models.PROTECT)


class UpdatesRequisitionMetadataModelMixin(UpdatesMetadataModelMixin):
    """A model mixin used on Requisition models to enable them to
    update metadata upon save and delete.
    """

    metadata_updater_cls: RequisitionMetadataUpdater = RequisitionMetadataUpdater
    metadata_category: str = REQUISITION

    @property
    def metadata_updater(self: RequisitionModel) -> RequisitionMetadataUpdater:
        """Returns an instance of RequisitionMetadataUpdater."""
        opts = dict(
            related_visit=self.related_visit,
            target_model=self._meta.label_lower,
            target_panel=self.panel,
        )
        return self.metadata_updater_cls(**opts)

    @property
    def metadata_query_options(self: RequisitionModel) -> dict:
        options = super().metadata_query_options
        options.update({"panel_name": self.panel.name})
        return options

    @property
    def metadata_default_entry_status(self: RequisitionModel) -> str:
        """Returns a string that represents the configured
        entry status of the requisition in the visit schedule.
        """
        requisitions_prn = self.metadata_visit_object.requisitions_prn
        if self.related_visit.visit_code_sequence != 0:
            requisitions = (
                self.metadata_visit_object.requisitions_unscheduled + requisitions_prn
            )
        else:
            requisitions = self.metadata_visit_object.requisitions + requisitions_prn
        requisition = [r for r in requisitions if r.panel.name == self.panel.name][0]
        return REQUIRED if requisition.required else NOT_REQUIRED

    @property
    def metadata_model(self: RequisitionModel) -> Type[RequisitionMetadata]:
        """Returns the metadata model associated with self."""
        metadata_model = "edc_metadata.requisitionmetadata"
        return django_apps.get_model(metadata_model)

    class Meta:
        abstract = True
