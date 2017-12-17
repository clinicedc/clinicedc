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
        if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
            self.run_metadata_rules_for_crf()

    def run_metadata_rules_for_crf(self):
        """Runs all the rule groups for this app label.
        """
        self.visit.run_metadata_rules(visit=self.visit)

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
        obj.entry_status = self.metadata_default_entry_status or REQUIRED
        obj.report_datetime = None
        obj.save()

        if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
            self.run_metadata_rules_for_crf()

    @property
    def metadata_default_entry_status(self):
        """Returns a string that represents the default entry status
        of the crf in the visit schedule.
        """
        if self.visit.visit_code_sequence != 0:
            crfs = self.metadata_visit_object.crfs_unscheduled
        else:
            crfs = self.metadata_visit_object.crfs
        try:
            crf = [c for c in crfs if c.model == self._meta.label_lower][0]
        except IndexError as e:
            raise MetadataError(
                f'{self._meta.label_lower}. Got {e}') from e
        return REQUIRED if crf.required else NOT_REQUIRED

    @property
    def metadata_visit_object(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit.visit_schedule_name)
        schedule = visit_schedule.get_schedule(
            schedule_name=self.visit.schedule_name)
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
