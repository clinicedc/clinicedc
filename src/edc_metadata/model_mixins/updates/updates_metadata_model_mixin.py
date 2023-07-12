from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.db import models
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import CRF, REQUIRED
from ...metadata_updater import MetadataUpdater

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin as Base
    from edc_visit_schedule import Visit

    from ...models import CrfMetadata, RequisitionMetadata
    from ..creates import CreatesMetadataModelMixin
    from .updates_crf_metadata_model_mixin import UpdatesCrfMetadataModelMixin
    from .updates_requisition_metadata_model_mixin import (
        UpdatesRequisitionMetadataModelMixin,
    )

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass

    class CrfModel(UpdatesCrfMetadataModelMixin, Base):
        related_visit = models.ForeignKey(RelatedVisitModel, on_delete=models.PROTECT)

    class RequisitionModel(UpdatesRequisitionMetadataModelMixin, Base):
        related_visit = models.ForeignKey(RelatedVisitModel, on_delete=models.PROTECT)


class MetadataError(Exception):
    pass


class UpdatesMetadataModelMixin(models.Model):
    """A model mixin used on CRF models to enable them to
    update metadata upon save and delete.
    """

    metadata_updater_cls = MetadataUpdater
    metadata_category: str = CRF

    def metadata_update(self: CrfModel | RequisitionModel, entry_status: str = None) -> None:
        """Updates metatadata."""
        self.metadata_updater.get_and_update(entry_status=entry_status)

    def run_metadata_rules_for_crf(
        self: CrfModel | RequisitionModel, allow_create: bool | None = None
    ) -> None:
        """Runs all the metadata rules for this timepoint."""
        self.related_visit.run_metadata_rules(allow_create=allow_create)

    @property
    def metadata_updater(self: CrfModel | RequisitionModel) -> MetadataUpdater:
        """Returns an instance of MetadataUpdater.

        Override
        """
        raise NotImplementedError("Method not implemented")

    @property
    def metadata_query_options(self: CrfModel | RequisitionModel) -> dict:
        options = self.related_visit.metadata_query_options
        options.update(
            {
                "subject_identifier": self.related_visit.subject_identifier,
                "model": self._meta.label_lower,
            }
        )
        return options

    @property
    def metadata_model(
        self: CrfModel | RequisitionModel,
    ) -> Type[CrfMetadata] | Type[RequisitionMetadata]:
        """Returns the metadata model associated with self.

        Override
        """
        raise NotImplementedError("Method not implemented")

    @property
    def metadata_default_entry_status(self: CrfModel | RequisitionModel) -> str:
        """Returns a string that represents the default entry status
        of the CRF in the visit schedule.

        Override
        """
        raise NotImplementedError("Method not implemented")

    def metadata_reset_on_delete(self: CrfModel | RequisitionModel) -> None:
        """Sets this model instance`s metadata model instance
        to its original entry_status.
        """
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        try:
            obj.entry_status = self.metadata_default_entry_status
        except IndexError:
            # if IndexError, implies CRF is not listed in
            # the visit schedule, so remove it.
            # for example, this is a PRN form
            obj.delete()
        else:
            obj.entry_status = self.metadata_default_entry_status or REQUIRED
            obj.report_datetime = None
            obj.save()

    @property
    def metadata_visit_object(self: CrfModel | RequisitionModel) -> Visit:
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.related_visit.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(self.related_visit.schedule_name)
        return schedule.visits.get(self.related_visit.visit_code)

    class Meta:
        abstract = True
