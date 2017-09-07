from django.apps import apps as django_apps
from django.db import models
from edc_metadata_rules import MetadataRuleEvaluator
from edc_visit_schedule import site_visit_schedules

from ...constants import KEYED
from ...metadata import Metadata


class CreatesMetadataModelMixin(models.Model):
    """A mixin to enable a model to create metadata on save.

    Typically this is a Visit model.
    """

    metadata_cls = Metadata
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
            visit_code=visit.code)
        return options

    @property
    def metadata(self):
        """Returns a dictionary of metadata querysets for each
        metadata category.
        """
        app_config = django_apps.get_app_config('edc_metadata')
        return app_config.get_metadata(
            self.subject_identifier, **self.metadata_query_options)

    def metadata_delete_for_visit(self, instance=None):
        """Deletes metadata for a visit when the visit instance
        is deleted.
        """
        metadata_crf_model = django_apps.get_app_config(
            'edc_metadata').crf_model
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(
            schedule_name=self.schedule_name)
        visit = schedule.visits.get(self.visit_code)
        metadata_crf_model.objects.filter(
            subject_identifier=instance.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            visit_code=visit.code).exclude(entry_status=KEYED).delete()

    class Meta:
        abstract = True
