from django.db.models import options
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .choices import ENTRY_STATUS
from .constants import REQUIRED, NOT_REQUIRED, KEYED

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('metadata_category',)


class UpdateMetadataModelMixin(models.Model):
    """Updates the metadata instance associated with self."""

    def metadata_update(self):
        app_config = django_apps.get_app_config('edc_meta_data')
        app_config.get_model(self._meta.metadata_category)
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        obj.entry_status = KEYED
        obj.report_datetime = self.report_datetime
        obj.save()
        self.visit.metadata_run_rules()

    def metadata_delete(self):
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        obj.entry_status = REQUIRED
        obj.report_datetime = None
        obj.save()
        self.visit.metadata_run_rules()

    @property
    def metadata_query_options(self):
        options = self.visit.metadata_query_options
        if self.metadata_model._meta.metadata_category == 'requisition':
            options.update({'panel_name': self.panel.name})
        options.update({
            'subject_identifier': self.visit.subject_identifier,
            'model': self._meta.label_lower})
        return options

    @property
    def metadata_model(self):
        """Returns the metadata model associated with self.

        Note: if self is a requsition, then assumes there is a FK to \'panel\'.
        """
        app_config = django_apps.get_app_config('edc_metadata')
        try:
            panel_name = self.panel.name
        except AttributeError:
            panel_name = None
        return app_config.get_model(panel_name=panel_name)

    class Meta:
        abstract = True
        metadata_category = None


class CreatesMetadataModelMixin(models.Model):

    @property
    def metadata_query_options(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.appointment.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.appointment.schedule_name)
        visit = schedule.get_visit(self.appointment.visit_code)
        options = dict(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            visit_code=visit.code)
        return options

    def metadata_create(self):
        """Creates Crf and Requisition meta data for the subject visit.

        Assumes 'appointment' FK exists."""

        app_config = django_apps.get_app_config('edc_metadata')
        metadata_crf_model = app_config.crf_model
        if not metadata_crf_model._meta.unique_together:
            raise ImproperlyConfigured('{}.unique_together constraint not set.'.format(metadata_crf_model._meta.label_lower))
        metadata_requisition_model = app_config.requisition_model
        if not metadata_requisition_model._meta.unique_together:
            raise ImproperlyConfigured('{}.unique_together constraint not set.'.format(metadata_requisition_model._meta.label_lower))
        visit_schedule = site_visit_schedules.get_visit_schedule(self.appointment.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.appointment.schedule_name)
        visit = schedule.get_visit(self.appointment.visit_code)
        if getattr(self, app_config.reason_field) in app_config.delete_on_reasons:
            metadata_crf_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
            metadata_requisition_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
        elif getattr(self, app_config.reason_field) in app_config.create_on_reasons:
            metadata_crf_model = django_apps.get_app_config('edc_metadata').crf_model
            metadata_requisition_model = django_apps.get_app_config('edc_metadata').requisition_model
            visit_schedule = site_visit_schedules.get_visit_schedule(self.appointment.visit_schedule_name)
            schedule = visit_schedule.get_schedule(self.appointment.schedule_name)
            visit = schedule.get_visit(self.appointment.visit_code)
            options = self.metadata_query_options
            options.update({'subject_identifier': self.subject_identifier})
            for crf in visit.crfs:
                options.update({'model': crf.model._meta.label_lower})
                try:
                    metadata_crf_model.objects.get(**options)
                except metadata_crf_model.DoesNotExist:
                    metadata_crf_model.objects.create(
                        entry_status=REQUIRED if crf.required else NOT_REQUIRED,
                        **options)
            for requisition in visit.requisitions:
                options.update({
                    'model': requisition.model._meta.label_lower,
                    'panel_name': requisition.panel.name})
                try:
                    metadata_requisition_model.objects.get(**options)
                except metadata_requisition_model.DoesNotExist:
                    metadata_requisition_model.objects.create(
                        entry_status=REQUIRED if requisition.required else NOT_REQUIRED,
                        **options)

    def metadata_run_rules(self):
        pass

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


class BaseMetadataModelMixin(models.Model):

    """ Mixin for CrfMetadata and RequisitionMetadata models to be created in the local app.

    Use the specific model mixins below.
    """

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        editable=False)

    visit_schedule_name = models.CharField(max_length=25)

    schedule_name = models.CharField(max_length=25)

    visit_code = models.CharField(max_length=25)

    model = models.CharField(max_length=50)

    current_entry_title = models.CharField(
        max_length=250,
        null=True)

    entry_status = models.CharField(
        max_length=25,
        choices=ENTRY_STATUS,
        default=REQUIRED,
        db_index=True)

    due_datetime = models.DateTimeField(
        null=True,
        blank=True)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)

    entry_comment = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    close_datetime = models.DateTimeField(
        null=True,
        blank=True)

    fill_datetime = models.DateTimeField(
        null=True,
        blank=True)

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name, self.visit_code, self.model)

    def is_required(self):
        return self.entry_status != NOT_REQUIRED

    def is_not_required(self):
        return not self.is_required()

    class Meta:
        abstract = True
        unique_together = (('subject_identifier', 'visit_schedule_name', 'schedule_name', 'visit_code', 'model'), )


class CrfMetadataModelMixin(BaseMetadataModelMixin):

    def __str__(self):
        return 'CrfMeta {}.{} {} {}'.format(self.model, self.visit_code, self.entry_status, self.subject_identifier)

    class Meta(BaseMetadataModelMixin.Meta):
        abstract = True
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"


class RequisitionMetadataModelMixin(BaseMetadataModelMixin):

    panel_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return 'RequisitionMeta {}.{}.{} {} {}'.format(
            self.model, self.visit_code, self.panel_name, self.entry_status, self.subject_identifier)

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name,
                self.visit_code, self.model, self.panel_name)

    class Meta(BaseMetadataModelMixin.Meta):
        abstract = True
        verbose_name = "Requisition Meta Data"
        verbose_name_plural = "Requisition Meta Data"
        unique_together = (('subject_identifier', 'visit_schedule_name', 'schedule_name',
                           'visit_code', 'model', 'panel_name'), )
