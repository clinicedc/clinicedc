import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.db import OperationalError

from edc_metadata.models import CrfMetadata, RequisitionMetadata

from edc_metadata.constants import NOT_REQUIRED


style = color_style()


class DashboardError(Exception):
    pass


class MetaDataMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            NOT_REQUIRED=NOT_REQUIRED,
            crfs=self.crfs,
            requisitions=self.requisitions
        )
        return context

    @property
    def crf_metadata_set(self):
        return CrfMetadata.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_code=self.appointment.visit_code).order_by('show_order')

    @property
    def next_url_parameters(self):
        """Add these additional parameters to the next url"""
        parameters = super().next_url_parameters
        parameters.update({
            'crfs': ['subject_identifier', 'appointment']})
        return parameters

    @property
    def crfs(self):
        crfs = []
        if self.appointment:
            for metadata in self.crf_metadata_set:
                try:
                    obj = None
                    options = {
                        '{}__appointment'.format(
                            metadata.model_class.visit_model_attr()): self.appointment}
                    try:
                        obj = metadata.model_class.objects.get(**options)
                    except AttributeError as e:
                        self.delete_invalid_metadata(metadata, e)
                    except LookupError as e:
                        self.handle_lookup_error(metadata)
                    except OperationalError as e:
                        self.handle_operational_error(metadata)
                    else:
                        metadata.instance = obj
                        metadata.visit_attr_name = metadata.model_class.visit_model_attr()
                        metadata.visit = getattr(
                            metadata.instance, metadata.visit_attr_name)
                        metadata.url = obj.get_absolute_url()
                        metadata.title = obj._meta.verbose_name
                except metadata.model_class.DoesNotExist:
                    metadata.instance = None
                    try:
                        metadata.visit_attr_name = metadata.model_class.visit_model_attr()
                    except AttributeError as e:
                        raise ImproperlyConfigured(
                            'Model {} is not configured as a CRF model. '
                            'Correct or remove this model from your schedule. Got {}'.format(
                                metadata.model_class()._meta.label_lower, str(e)))
                    metadata.url = metadata.model_class().get_absolute_url()
                    metadata.title = metadata.model_class()._meta.verbose_name
                metadata.next_url = self.get_next_url(key='crfs')
                crfs.append(metadata)
        return crfs

    @property
    def requisition_metadata_set(self):
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_code=self.appointment.visit_code)

    @property
    def requisitions(self):
        requisitions = []
        if self.appointment:
            for metadata in self.requisition_metadata_set:
                try:
                    obj = None
                    options = {
                        '{}__appointment'.format(
                            metadata.model_class.visit_model_attr()): self.appointment,
                        'panel_name': metadata.panel_name}

                    obj = metadata.model_class.objects.get(**options)
                    metadata.instance = obj
                    metadata.url = obj.get_absolute_url()
                    metadata.title = obj._meta.verbose_name
                except metadata.model_class.DoesNotExist:
                    metadata.instance = None
                    metadata.url = metadata.model_class().get_absolute_url()
                    metadata.title = metadata.model_class()._meta.verbose_name
                requisitions.append(metadata)
        return requisitions

    def handle_lookup_error(self, metadata):
        # getting here means you changed a table name
        metadata.delete()
        sys.stdout.write(style.NOTICE(
            'Dashboard detected and deleted an invalid crf '
            'entry in crf metadata. Got {}'.format(metadata)))
        sys.stdout.flush()

    def handle_operational_error(self, metadata):
        # getting here means you changed a table name but havent migrated the change
        metadata.delete()
        sys.stdout.write(style.NOTICE(
            'Dashboard detected and deleted an invalid crf model '
            'name entry in crf metadata. Got {}'.format(metadata)))
        sys.stdout.flush()

    def delete_invalid_metadata(self, metadata, exception):
        if 'visit_model_attr' not in str(exception):
            raise DashboardError(str(exception))
        metadata.delete()
        sys.stdout.write(style.NOTICE(
            'Dashboard detected and deleted a non-crf entry in '
            'crf metadata. Got {}'.format(metadata)))
        sys.stdout.flush()
