from django.db import models
from edc_metadata_rules import MetadataRuleEvaluator

from ...constants import KEYED, REQUISITION, CRF
from ...metadata import Metadata, Destroyer, DeleteMetadataError
from ...metadata import RequisitionMetadataGetter, CrfMetadataGetter


class CreatesMetadataModelMixin(models.Model):
    """A model mixin for visit models to enable them to
    create metadata on save.
    """

    metadata_cls = Metadata
    metadata_destroyer_cls = Destroyer
    metadata_rule_evaluator_cls = MetadataRuleEvaluator

    def metadata_create(self):
        """Creates metadata, called by post_save signal.
        """
        metadata = self.metadata_cls(visit_model_instance=self, update_keyed=True)
        metadata.prepare()

    def run_metadata_rules(self):
        """Runs all the metadata rules.

        Initially called by post_save signal.

        Also called by post_save signal after metadata is updated.
        """
        metadata_rule_evaluator = self.metadata_rule_evaluator_cls(
            visit_model_instance=self
        )
        metadata_rule_evaluator.evaluate_rules()

    @property
    def metadata_query_options(self):
        """Returns a dictionary of query options needed select
        the visit model instance
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
    def metadata(self):
        """Returns a dictionary of metadata querysets for each
        metadata category (CRF or REQUISITION).
        """
        metadata = {}
        getter = CrfMetadataGetter(appointment=self.appointment)
        metadata[CRF] = getter.metadata_objects
        getter = RequisitionMetadataGetter(appointment=self.appointment)
        metadata[REQUISITION] = getter.metadata_objects
        return metadata

    def metadata_delete_for_visit(self):
        """Deletes metadata for a visit when the visit is deleted.

        See signals.
        """
        for key in [CRF, REQUISITION]:
            if [obj for obj in self.metadata[key] if obj.entry_status == KEYED]:
                raise DeleteMetadataError(
                    f"Metadata cannot be deleted. {key}s have been "
                    f"keyed. Got {repr(self)}."
                )
        destroyer = self.metadata_destroyer_cls(visit_model_instance=self)
        destroyer.delete()

    class Meta:
        abstract = True
