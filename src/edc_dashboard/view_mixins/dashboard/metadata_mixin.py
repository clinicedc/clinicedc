import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.db import OperationalError

from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .consent_mixin import ConsentMixin


style = color_style()


class DashboardError(Exception):
    pass


class MetaDataMixin(ConsentMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            crfs=self.crfs,
            requisitions=self.requisitions)
        return context

    @property
    def crfs(self):
        crfs = []
        if self.appointment:
            crf_meta_datas = CrfMetadata.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_code=self.appointment.visit_code).order_by('show_order')
            for crf in crf_meta_datas:
                try:
                    obj = None
                    try:
                        options = {
                            '{}__appointment'.format(
                                crf.model_class.visit_model_attr()): self.appointment}
                        obj = crf.model_class.objects.get(**options)
                        crf.instance = obj
                        crf.visit_attr_name = crf.model_class.visit_model_attr()
                        crf.visit = getattr(crf.instance, crf.visit_attr_name)
                        crf.url = obj.get_absolute_url()
                        crf.title = obj._meta.verbose_name
                    except AttributeError as e:
                        if 'visit_model_attr' not in str(e):
                            raise DashboardError(str(e))
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted a non-crf entry in '
                            'crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                    except LookupError as e:
                        # getting here means you changed a table name
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted an invalid crf '
                            'entry in crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                    except OperationalError as e:
                        # getting here means you changed a table name but havent migrated the change
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted an invalid crf model '
                            'name entry in crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                except crf.model_class.DoesNotExist:
                    crf.instance = None
                    try:
                        crf.visit_attr_name = crf.model_class.visit_model_attr()
                    except AttributeError as e:
                        raise ImproperlyConfigured(
                            'Model {} is not configured as a CRF model. '
                            'Correct or remove this model from your schedule. Got {}'.format(
                                crf.model_class()._meta.label_lower, str(e)))
                    crf.url = crf.model_class().get_absolute_url()
                    crf.title = crf.model_class()._meta.verbose_name
                crfs.append(crf)
        return crfs

    @property
    def requisitions(self):
        requisitions = []
        if self.appointment:
            requisition_meta_data = RequisitionMetadata.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_code=self.appointment.visit_code)
            for requisition in requisition_meta_data:
                try:
                    obj = None
                    options = {
                        '{}__appointment'.format(
                            requisition.model_class.visit_model_attr()): self.appointment,
                        'panel_name': requisition.panel_name}

                    obj = requisition.model_class.objects.get(**options)
                    requisition.instance = obj
                    requisition.url = obj.get_absolute_url()
                    requisition.title = obj._meta.verbose_name
                except requisition.model_class.DoesNotExist:
                    requisition.instance = None
                    requisition.url = requisition.model_class().get_absolute_url()
                    requisition.title = requisition.model_class()._meta.verbose_name
                requisitions.append(requisition)
        return requisitions
