from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import REQUIRED, NOT_REQUIRED
from ...exceptions import CreatesMetadataError

from ..rules import MetadataRulesModelMixin


class CreatesMetadataModelMixin(MetadataRulesModelMixin, models.Model):
    """A mixin to enable a model to create metadata on save.

    Typically this is a Visit model."""

    @property
    def metadata_query_options(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.schedule_name)
        visit = schedule.get_visit(self.visit_code)
        options = dict(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            visit_code=visit.code)
        return options

    @property
    def metadata(self):
        """Returns a dictionary of metadata querysets for each metadata category."""
        app_config = django_apps.get_app_config('edc_metadata')
        return app_config.get_metadata(
            self.subject_identifier, **self.metadata_query_options)

    def metadata_create(self, sender=None, instance=None):
        """Creates Crf and Requisition meta data for the subject visit."""
        metadata_exists = True
        app_config = django_apps.get_app_config('edc_metadata')
        metadata_crf_model = app_config.crf_model
        if not metadata_crf_model._meta.unique_together:
            raise ImproperlyConfigured(
                '{}.unique_together constraint not set.'.format(metadata_crf_model._meta.label_lower))
        metadata_requisition_model = app_config.requisition_model
        if not metadata_requisition_model._meta.unique_together:
            raise ImproperlyConfigured(
                '{}.unique_together constraint not set.'.format(metadata_requisition_model._meta.label_lower))
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.schedule_name)
        visit = schedule.get_visit(self.visit_code)
        try:
            reason_field = app_config.reason_field[self._meta.label_lower]
            reason = getattr(self, reason_field)
        except KeyError as e:
            raise CreatesMetadataError(
                'Unable to determine the reason field for model {}. Got KeyError({}). '
                'edc_metadata.AppConfig reason_field = {}'.format(
                    self._meta.label_lower, str(e), app_config.reason_field))
        except AttributeError:
            raise CreatesMetadataError(
                'Invalid reason field. Expected attribute {}.{}. Got AttributeError({}). '
                'edc_metadata.AppConfig reason_field = {}'.format(
                    reason_field, self._meta.label_lower, str(e), app_config.reason_field))
        if reason in app_config.delete_on_reasons:
            metadata_crf_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
            metadata_requisition_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
            metadata_exists = False
        elif reason in app_config.create_on_reasons:
            metadata_crf_model = django_apps.get_app_config('edc_metadata').crf_model
            metadata_requisition_model = django_apps.get_app_config('edc_metadata').requisition_model
            visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
            schedule = visit_schedule.get_schedule(self.schedule_name)
            visit = schedule.get_visit(self.visit_code)
            options = self.metadata_query_options
            options.update({'subject_identifier': self.subject_identifier})
            metadata_crfs = []
            for crf in visit.crfs:
                options.update({'model': crf.model._meta.label_lower})
                try:
                    metadata_crf_model.objects.get(**options)
                except metadata_crf_model.DoesNotExist:
                    metadata_crfs.append(metadata_crf_model.objects.create(
                        entry_status=REQUIRED if crf.required else NOT_REQUIRED,
                        show_order=crf.show_order,
                        **options))
            for requisition in visit.requisitions:
                options.update({
                    'model': requisition.model._meta.label_lower,
                    'panel_name': requisition.panel.name})
                try:
                    metadata_requisition_model.objects.get(**options)
                except metadata_requisition_model.DoesNotExist:
                    metadata_requisition_model.objects.create(
                        entry_status=REQUIRED if requisition.required else NOT_REQUIRED,
                        show_order=requisition.show_order,
                        **options)
        else:
            raise CreatesMetadataError(
                'Undefined \'reason\'. Cannot create metadata. Got {}.{} = \'{}\'. '
                'Check field value and/or edc_metadata.AppConfig.reason_field.'.format(
                    self._meta.label_lower,
                    app_config.reason_field[self._meta.label_lower],
                    getattr(self, app_config.reason_field[self._meta.label_lower])))
        return metadata_exists

# TODO:
#     def metadata_require(self):
#         if self.survival_status == DEAD:
#             self.require_death_report()
#         else:
#             self.undo_require_death_report()
#         if self.study_status == OFF_STUDY:
#             self.require_off_study_report()
#         else:
#             self.undo_require_off_study_report()

    class Meta:
        abstract = True
