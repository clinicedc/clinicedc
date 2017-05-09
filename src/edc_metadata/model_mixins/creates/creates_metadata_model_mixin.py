from django.apps import apps as django_apps
from django.db import models

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import KEYED
from ...metadata import Metadata
from ..rules import MetadataRulesModelMixin


class CreatesMetadataModelMixin(MetadataRulesModelMixin, models.Model):
    """A mixin to enable a model to create metadata on save.

    Typically this is a Visit model.
    """

    @property
    def metadata_query_options(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.schedule_name)
        visit = schedule.get_visit(self.visit_code)
        options = dict(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
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

    def metadata_create(self, sender=None, instance=None):
        metadata = Metadata(visit_instance=self, update_keyed=True)
        return metadata.prepare()

    def metadata_delete_for_visit(self, instance=None):
        """Deletes metadata for a visit when the visit instance
        is deleted.
        """
        metadata_crf_model = django_apps.get_app_config(
            'edc_metadata').crf_model
        # TODO: delete requisitions
#         metadata_requisition_model = django_apps.get_app_config(
#             'edc_metadata').requisition_model
        visit_schedule = site_visit_schedules.get_visit_schedule(
            self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.schedule_name)
        visit = schedule.get_visit(self.visit_code)
        metadata_crf_model.objects.filter(
            subject_identifier=instance.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            visit_code=visit.code).exclude(entry_status=KEYED).delete()

    class Meta:
        abstract = True
