from django.apps import apps as django_apps
from django.db import models
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import REQUIRED, NOT_REQUIRED


class MetadataError(Exception):
    pass


class UpdatesMetadataModelMixin(models.Model):

    updater_cls = None
    metadata_category = None

    def metadata_update(self, entry_status=None):
        """Updates metatadata.
        """
        self.metadata_updater.update(entry_status=entry_status)

    def run_metadata_rules_for_crf(self):
        """Runs all the metadata rules.
        """
        self.visit.run_metadata_rules()

    @property
    def metadata_updater(self):
        """Returns an instance of MetadataUpdater.
        """
        return self.updater_cls(
            visit=self.visit,
            target_model=self._meta.label_lower)

    def metadata_reset_on_delete(self):
        """Sets the metadata instance to its original state.
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
    def metadata_default_entry_status(self):
        """Returns a string that represents the default entry status
        of the CRF in the visit schedule.
        """
        crfs_prn = self.metadata_visit_object.crfs_prn
        if self.visit.visit_code_sequence != 0:
            crfs = self.metadata_visit_object.crfs_unscheduled + crfs_prn
        else:
            crfs = self.metadata_visit_object.crfs + crfs_prn
        crf = [c for c in crfs if c.model == self._meta.label_lower][0]
        return REQUIRED if crf.required else NOT_REQUIRED

    @property
    def metadata_visit_object(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit.visit_schedule_name)
        schedule = visit_schedule.schedules.get(self.visit.schedule_name)
        return schedule.visits.get(self.visit.visit_code)

    @property
    def metadata_query_options(self):
        options = self.visit.metadata_query_options
        options.update({
            'subject_identifier': self.visit.subject_identifier,
            'model': self._meta.label_lower})
        return options

    @property
    def metadata_model(self):
        """Returns the metadata model associated with self.
        """
        app_config = django_apps.get_app_config('edc_metadata')
        return app_config.get_metadata_model(self.metadata_category)

    class Meta:
        abstract = True
