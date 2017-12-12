from django.apps import apps as django_apps
from django.db import models
from edc_metadata_rules import MetadataRuleEvaluator

from ...constants import KEYED, REQUISITION, CRF
from ...metadata import Metadata, Destroyer, DeleteMetadataError
from ...metadata import RequisitionMetadataGetter, CrfMetadataGetter


class CreatesMetadataModelMixin(models.Model):
    """A mixin to enable a model to create metadata on save.

    Typically this is a Visit model.
    """

    metadata_cls = Metadata
    metadata_destroyer_cls = Destroyer
    metadata_rule_evaluator_cls = MetadataRuleEvaluator

    def metadata_create(self, sender=None, instance=None):
        metadata = self.metadata_cls(visit=self, update_keyed=True)
        metadata.prepare()
        if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
            self.run_metadata_rules()

    def run_metadata_rules(self, visit=None):
        """Runs all the rule groups.
        """
        visit = visit or self
        metadata_rule_evaluator = self.metadata_rule_evaluator_cls(
            visit=visit)
        metadata_rule_evaluator.evaluate_rules()

    @property
    def metadata_query_options(self):
        visit = self.visits.get(self.visit_code)
        options = dict(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=visit.code,
            visit_code_sequence=self.visit_code_sequence)
        return options

    @property
    def metadata(self):
        """Returns a dictionary of metadata querysets for each
        metadata category.
        """
        metadata = {}
        for name, getter_cls in [
                (CRF, CrfMetadataGetter), (REQUISITION, RequisitionMetadataGetter)]:
            getter = getter_cls(appointment=self.appointment)
            metadata[name] = getter.metadata_objects
        return metadata

    def metadata_delete_for_visit(self):
        """Deletes metadata for a visit when the visit instance
        is deleted.

        See signals.
        """
        for key in [CRF, REQUISITION]:
            if [obj for obj in self.metadata[key] if obj.entry_status == KEYED]:
                raise DeleteMetadataError(
                    f'Metadata cannot be deleted. {key}s have been keyed. Got {repr(self)}.')
        destroyer = self.metadata_destroyer_cls(visit=self)
        destroyer.delete()

    class Meta:
        abstract = True
