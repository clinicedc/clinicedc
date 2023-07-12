from __future__ import annotations

from django.db import models
from edc_visit_tracking.model_mixins import VisitModelMixin

from ...constants import CRF, KEYED, REQUISITION
from ...metadata import (
    CrfMetadataGetter,
    DeleteMetadataError,
    Destroyer,
    Metadata,
    RequisitionMetadataGetter,
)
from ...metadata_rules import MetadataRuleEvaluator


class CreatesMetadataModelMixin(models.Model):
    """A model mixin for visit models to enable them to
    create metadata on save.
    """

    metadata_cls: Metadata = Metadata
    metadata_destroyer_cls: Destroyer = Destroyer
    metadata_rule_evaluator_cls: MetadataRuleEvaluator = MetadataRuleEvaluator

    def metadata_create(self) -> None:
        """Creates metadata, called by post_save signal."""
        metadata = self.metadata_cls(related_visit=self, update_keyed=True)
        metadata.prepare()

    def run_metadata_rules(self, allow_create: bool | None = None) -> None:
        """Runs all the metadata rules.

        Initially called by post_save signal.

        Also called by post_save signal after metadata is updated.
        """
        metadata_rule_evaluator = self.metadata_rule_evaluator_cls(
            related_visit=self, allow_create=allow_create
        )
        metadata_rule_evaluator.evaluate_rules()

    @property
    def metadata_query_options(self: VisitModelMixin) -> dict:
        """Returns a dictionary of query options needed select
        the related_visit.
        """
        visit = self.visits.get(self.appointment.visit_code)
        options = dict(
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=visit.code,
            visit_code_sequence=self.appointment.visit_code_sequence,
            timepoint=self.appointment.timepoint,
        )
        return options

    @property
    def metadata(self: VisitModelMixin) -> dict:
        """Returns a dictionary of metadata querysets for each
        metadata category (CRF or REQUISITION).
        """
        metadata = {}
        getter = CrfMetadataGetter(self.appointment)
        metadata[CRF] = getter.metadata_objects
        getter = RequisitionMetadataGetter(self.appointment)
        metadata[REQUISITION] = getter.metadata_objects
        return metadata

    def metadata_delete_for_visit(self) -> None:
        """Deletes metadata for a visit when the visit is deleted.

        See signals.
        """
        for key in [CRF, REQUISITION]:
            if [obj for obj in self.metadata[key] if obj.get_entry_status() == KEYED]:
                raise DeleteMetadataError(
                    f"Metadata cannot be deleted. {key}s have been "
                    f"keyed. Got {repr(self)}."
                )
        destroyer = self.metadata_destroyer_cls(related_visit=self)
        destroyer.delete()

    class Meta:
        abstract = True
