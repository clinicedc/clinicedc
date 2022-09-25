from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db import models
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import CRF, NOT_REQUIRED, REQUIRED, REQUISITION
from ...metadata_updater import MetadataUpdater

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin
    from edc_visit_schedule import Visit

    from ...models import CrfMetadata, RequisitionMetadata


class MetadataError(Exception):
    pass


class UpdatesMetadataModelMixin(models.Model):
    """A model mixin used on CRF models to enable them to
    update metadata upon save and delete.
    """

    metadata_updater_cls: MetadataUpdater = MetadataUpdater
    metadata_category: str = CRF

    def metadata_update(self: CrfModelMixin, entry_status: str = None) -> None:
        """Updates metatadata."""
        self.metadata_updater.update(entry_status=entry_status)

    def run_metadata_rules_for_crf(self: CrfModelMixin) -> None:
        """Runs all the metadata rules."""
        self.related_visit.run_metadata_rules()

    @property
    def metadata_updater(self: CrfModelMixin) -> None:
        """Returns an instance of MetadataUpdater."""
        return self.metadata_updater_cls(
            related_visit=self.related_visit, target_model=self._meta.label_lower
        )

    def metadata_reset_on_delete(self: CrfModelMixin) -> None:
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
    def metadata_default_entry_status(self: CrfModelMixin) -> str:
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

    @property
    def metadata_visit_object(self: CrfModelMixin) -> Visit:
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.related_visit.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(self.related_visit.schedule_name)
        return schedule.visits.get(self.related_visit.visit_code)

    @property
    def metadata_query_options(self: CrfModelMixin) -> dict:
        options = self.related_visit.metadata_query_options
        options.update(
            {
                "subject_identifier": self.related_visit.subject_identifier,
                "model": self._meta.label_lower,
            }
        )
        return options

    @property
    def metadata_model(self: CrfModelMixin) -> CrfMetadata | RequisitionMetadata:
        """Returns the metadata model associated with self."""
        if self.metadata_category == CRF:
            metadata_model = "edc_metadata.crfmetadata"
        elif self.metadata_category == REQUISITION:
            metadata_model = "edc_metadata.requisitionmetadata"
        else:
            raise MetadataError(f"Unknown metadata catergory. Got {self.metadata_category}")
        return django_apps.get_model(metadata_model)

    class Meta:
        abstract = True
