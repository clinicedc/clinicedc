from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from edc_visit_schedule import site_visit_schedules

from .constants import NOT_REQUIRED, REQUIRED, KEYED
from .exceptions import CreatesMetadataError

app_config = django_apps.get_app_config('edc_metadata')


class Base:

    def __init__(self, visit_instance=None, metadata_crf_model=None,
                 metadata_requisition_model=None, **kwargs):
        self.visit_instance = visit_instance
        self.metadata_crf_model = metadata_crf_model or app_config.crf_model
        self.metadata_requisition_model = (
            metadata_requisition_model or app_config.requisition_model)
        if not self.metadata_crf_model._meta.unique_together:
            raise ImproperlyConfigured(
                f'{self.metadata_crf_model._meta.label_lower}.unique_together '
                'constraint not set.')
        if not self.metadata_requisition_model._meta.unique_together:
            raise ImproperlyConfigured(
                f'{self.metadata_requisition_model._meta.label_lower}.unique_together '
                'constraint not set.')


class CrfCreator(Base):

    def __init__(self, visit_instance=None, update_keyed=None, **kwargs):
        super().__init__(visit_instance=visit_instance, **kwargs)
        self.update_keyed = update_keyed

    def create(self, crf=None):
        """Creates metadata for a CRF.
        """
        options = self.visit_instance.metadata_query_options
        options.update(
            {'subject_identifier': self.visit_instance.subject_identifier,
             'model': crf.model._meta.label_lower})
        try:
            metadata_obj = self.metadata_crf_model.objects.get(**options)
        except self.metadata_crf_model.DoesNotExist:
            metadata_obj = self.metadata_crf_model.objects.create(
                entry_status=REQUIRED if crf.required else NOT_REQUIRED,
                show_order=crf.show_order, **options)
        if self.update_keyed and metadata_obj.entry_status != KEYED:
            if self.is_keyed(crf):
                metadata_obj.entry_status = KEYED
                metadata_obj.save()

    def is_keyed(self, crf=None):
        """Returns True if CRF is keyed.
        """
        model_class = django_apps.get_model(
            *crf.model._meta.label_lower.split('.'))
        return model_class.objects.filter(
            **{f'{model_class.visit_model_attr()}__visit_code':
               self.visit_instance.visit_code,
               f'{model_class.visit_model_attr()}__subject_identifier':
               self.visit_instance.subject_identifier}).exists()


class RequisitionCreator(Base):

    def __init__(self, visit_instance=None, update_keyed=None, **kwargs):
        super().__init__(visit_instance=visit_instance, **kwargs)
        self.update_keyed = update_keyed

    def create(self, requisition=None):
        """Creates metadata for a requisition.
        """
        options = self.visit_instance.metadata_query_options
        options.update(
            {'subject_identifier': self.visit_instance.subject_identifier,
             'model': requisition.model._meta.label_lower,
             'panel_name': requisition.panel.name})
        try:
            metadata_obj = self.metadata_requisition_model.objects.get(
                **options)
        except self.metadata_requisition_model.DoesNotExist:
            metadata_obj = self.metadata_requisition_model.objects.create(
                entry_status=REQUIRED if requisition.required else NOT_REQUIRED,
                show_order=requisition.show_order,
                **options)
        if (self.update_keyed and metadata_obj.entry_status != KEYED
                and self.is_keyed(requisition)):
            metadata_obj.entry_status = KEYED
            metadata_obj.save()

    def is_keyed(self, requisition=None):
        """Returns True if requisition is keyed.
        """
        model_class = django_apps.get_model(
            *requisition.model._meta.label_lower.split('.'))
        options = {
            f'{model_class.visit_model_attr()}__visit_code':
            self.visit_instance.visit_code,
            f'{model_class.visit_model_attr()}__subject_identifier':
            self.visit_instance.subject_identifier,
            f'panel_name': requisition.panel.name}
        return model_class.objects.filter(**options).exists()


class Creator:

    crf_creator_cls = CrfCreator
    requisition_creator_cls = RequisitionCreator

    def __init__(self, **kwargs):
        self.crf_creator = self.crf_creator_cls(**kwargs)
        self.requisition_creator = self.requisition_creator_cls(**kwargs)
        self.visit_instance = kwargs.get('visit_instance')
        schedule = site_visit_schedules.get_schedule(
            visit_schedule_name=self.visit_instance.visit_schedule_name,
            schedule_name=self.visit_instance.schedule_name)
        self.visit = schedule.visits.get(self.visit_instance.visit_code)

    def create(self):
        """Creates all CRF and requisition metadata for
        the visit instance.
        """
        for crf in self.visit.crfs:
            self.crf_creator.create(crf=crf)
        for requisition in self.visit.requisitions:
            self.requisition_creator.create(requisition=requisition)


class Destroyer(Base):

    def delete(self):
        """Deletes all CRF and requisition metadata for
        the visit instance.
        """
        self.metadata_crf_model.objects.filter(
            subject_identifier=self.visit_instance.subject_identifier,
            **self.visit_instance.metadata_query_options).delete()
        self.metadata_requisition_model.objects.filter(
            subject_identifier=self.visit_instance.subject_identifier,
            **self.visit_instance.metadata_query_options).delete()


class Metadata:

    creator_cls = Creator
    destroyer_cls = Destroyer

    def __init__(self, visit_instance=None, update_keyed=None, **kwargs):
        self.creator = self.creator_cls(
            visit_instance=visit_instance, update_keyed=update_keyed, **kwargs)
        self.destroyer = self.destroyer_cls(
            visit_instance=visit_instance, **kwargs)
        try:
            self.reason_field = app_config.reason_field[visit_instance._meta.label_lower]
        except KeyError as e:
            raise CreatesMetadataError(
                f'Unable to determine the reason field for model '
                f'{visit_instance._meta.label_lower}. Got {e}. '
                f'edc_metadata.AppConfig reason_field = {app_config.reason_field}') from e
        try:
            self.reason = getattr(visit_instance, self.reason_field)
        except AttributeError as e:
            raise CreatesMetadataError(
                f'Invalid reason field. Expected attribute {self.reason_field}. '
                f'{visit_instance._meta.label_lower}. Got {e}. '
                f'edc_metadata.AppConfig reason_field = {app_config.reason_field}') from e

    def prepare(self):
        """Creates or deletes metadata, depending on the visit reason,
        for the visit instance.
        """
        metadata_exists = False
        if self.reason in app_config.delete_on_reasons:
            self.destroyer.delete()
        elif self.reason in app_config.create_on_reasons:
            self.creator.create()
            metadata_exists = True
        else:
            visit_instance = self.creator.visit_instance
            raise CreatesMetadataError(
                f'Undefined \'reason\'. Cannot create metadata. Got '
                f'{visit_instance._meta.label_lower}.'
                f'{app_config.reason_field[visit_instance._meta.label_lower]} = '
                f'\'{getattr(visit_instance, app_config.reason_field[visit_instance._meta.label_lower])}\'. '
                'Check field value and/or edc_metadata.AppConfig.create_on_reasons/delete_on_reasons.')
        return metadata_exists
