from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_rule_groups.site_rule_groups import site_rule_groups
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .choices import ENTRY_STATUS
from .constants import REQUIRED, NOT_REQUIRED, KEYED
from .exceptions import CreatesMetadataError
from django.urls.base import reverse


class BaseUpdatesMetadataModelMixin(models.Model):

    def metadata_update(self, entry_status=None):
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        obj.entry_status = entry_status or KEYED
        obj.report_datetime = self.report_datetime
        obj.save()

    def metadata_delete(self):
        obj = self.metadata_model.objects.get(**self.metadata_query_options)
        obj.entry_status = self.metadata_default_entry_status or REQUIRED
        obj.report_datetime = None
        obj.save()

    @property
    def metadata_default_entry_status(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit.visit_schedule_name)
        schedule = visit_schedule.get_schedule(self.visit.schedule_name)
        visit = schedule.get_visit(self.visit.visit_code)
        if self.metadata_category == 'requisition':
            requisition = [r for r in visit.requisitions if r.panel.name == self.panel_name][0]
            default_entry_status = REQUIRED if requisition.required else NOT_REQUIRED
        elif self.metadata_category == 'crf':
            crf = [c for c in visit.crfs if c.model_label_lower == self._meta.label_lower][0]
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


class UpdatesCrfMetadataModelMixin(BaseUpdatesMetadataModelMixin):
    """A mixin used on Crf models to enable them to update metadata upon update/delete."""

    @property
    def metadata_category(self):
        return 'crf'

    class Meta:
        abstract = True


class UpdatesRequisitionMetadataModelMixin(BaseUpdatesMetadataModelMixin):
    """A mixin used on Requisition models to enable them to update metadata upon update/delete."""

    @property
    def metadata_category(self):
        return 'requisition'

    @property
    def metadata_query_options(self):
        options = super(UpdatesRequisitionMetadataModelMixin, self).metadata_query_options
        options.update({'panel_name': self.panel_name})
        return options

    class Meta:
        abstract = True


class CreatesMetadataModelMixin(models.Model):
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
        if getattr(self, app_config.reason_field[self._meta.label_lower]) in app_config.delete_on_reasons:
            metadata_crf_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
            metadata_requisition_model.objects.filter(
                subject_identifier=self.subject_identifier,
                **self.metadata_query_options).delete()
            metadata_exists = False
        elif getattr(self, app_config.reason_field[self._meta.label_lower]) in app_config.create_on_reasons:
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

    def metadata_update_for_model(self, model, entry_status, panel_name=None):
        """Updates metadata for a given model for this visit and subject_identifier."""
        model = django_apps.get_model(*model.split('.'))
        options = self.metadata_query_options
        options.update({
            'model': model._meta.label_lower,
            'subject_identifier': self.subject_identifier})
        if model().metadata_category == 'requisition':
            options.update({'panel_name': panel_name})
        try:
            obj = model().metadata_model.objects.get(**options)
            obj.entry_status = entry_status
            obj.save()
            return obj
        except model().metadata_model.DoesNotExist:
            return None

    def metadata_run_rules(self, source_model=None):
        """Runs all the rule groups for this app label."""
        for rule_group in site_rule_groups.registry.get(self._meta.app_label, []):
            if source_model:
                rule_group.run_for_source_model(self, source_model)
            else:
                rule_group.run_all(self)

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

    show_order = models.IntegerField(default=0)

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

    @property
    def model_class(self):
        return django_apps.get_model(*self.model.split('.'))

    class Meta:
        abstract = True


class CrfMetadataModelMixin(BaseMetadataModelMixin):

    def __str__(self):
        return 'CrfMeta {}.{} {} {}'.format(self.model, self.visit_code, self.entry_status, self.subject_identifier)

    @property
    def verbose_name(self):
        model = django_apps.get_model(self.model)
        return model._meta.verbose_name

    class Meta(BaseMetadataModelMixin.Meta):
        abstract = True
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"
        unique_together = (('subject_identifier', 'visit_schedule_name',
                            'schedule_name', 'visit_code', 'model'), )


class RequisitionMetadataModelMixin(BaseMetadataModelMixin):

    panel_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return 'RequisitionMeta {}.{}.{} {} {}'.format(
            self.model, self.visit_code, self.panel_name, self.entry_status, self.subject_identifier)

    @property
    def verbose_name(self):
        return self.panel_name

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name,
                self.visit_code, self.model, self.panel_name)

    class Meta(BaseMetadataModelMixin.Meta):
        abstract = True
        verbose_name = "Requisition Metadata"
        verbose_name_plural = "Requisition Metadata"
        unique_together = (('subject_identifier', 'visit_schedule_name', 'schedule_name',
                           'visit_code', 'model', 'panel_name'), )
