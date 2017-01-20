from django.apps import apps as django_apps
from django.db import models

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import REQUIRED, NOT_REQUIRED, KEYED, CRF, REQUISITION


class UpdatesMetadataModelMixin(models.Model):

    def metadata_update(self, entry_status=None):
        try:
            obj = self.metadata_model.objects.get(**self.metadata_query_options)
        except self.metadata_model.DoesNotExist as e:
            raise self.metadata_model.DoesNotExist(
                '{} Is \'{}\' scheduled for \'{}.{}.{}\'?'.format(
                    str(e), self.metadata_query_options.get('model'),
                    self.metadata_query_options.get('visit_schedule_name'),
                    self.metadata_query_options.get('schedule_name'),
                    self.metadata_query_options.get('visit_code')))
        obj.entry_status = entry_status or KEYED
        obj.report_datetime = self.report_datetime
        obj.save()

    def metadata_delete(self):
        """Sets the metadata instance to its original state."""
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        obj.entry_status = self.metadata_default_entry_status or REQUIRED
        obj.report_datetime = None
        obj.save()

    @property
    def metadata_default_entry_status(self):
        """Returns a string that represents the configured entry status
        of the crf or requisition in the visit schedule."""
        visit_schedule = site_visit_schedules.get_visit_schedule(
            self.visit.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.visit.schedule_name)
        visit = schedule.get_visit(self.visit.visit_code)
        if self.metadata_category == REQUISITION:
            requisition = [r for r in visit.requisitions
                           if r.panel.name == self.panel_name][0]
            default_entry_status = REQUIRED if requisition.required else NOT_REQUIRED
        elif self.metadata_category == CRF:
            crf = [c for c in visit.crfs
                   if c.model_label_lower == self._meta.label_lower][0]
            default_entry_status = REQUIRED if crf.required else NOT_REQUIRED
        return default_entry_status

    @property
    def metadata_query_options(self):
        options = self.visit.metadata_query_options
        options.update({
            'subject_identifier': self.visit.subject_identifier,
            'model': self._meta.label_lower})
        return options

    @property
    def metadata_model(self):
        """Returns the metadata model associated with self."""
        app_config = django_apps.get_app_config('edc_metadata')
        return app_config.get_metadata_model(self.metadata_category)

    class Meta:
        abstract = True
