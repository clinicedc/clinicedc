import sys

from django.core.management.color import color_style
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps
from django.urls.base import reverse

from edc_metadata.models import CrfMetadata, RequisitionMetadata

style = color_style()


class DashboardError(Exception):
    pass


class DashboardSubjectMixin:

    subject_dashboard_url_name = None

    def get_context_data(self, **kwargs):
        context = super(DashboardSubjectMixin, self).get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get('subject_identifier')
        self.show = self.kwargs.get('show')
        context.update(
            subject_identifier=self.subject_identifier,
            show=self.show,
            subject_dashboard_url_name=self.subject_dashboard_url_name)
        return context


class DashboardAppointmentMixin:

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').model

    def get_context_data(self, **kwargs):
        context = super(DashboardAppointmentMixin, self).get_context_data(**kwargs)
        pk = self.kwargs.get('selected_appointment')
        try:
            self.selected_appointment = self.appointment_model.objects.get(pk=pk)
            appointments = []
        except self.appointment_model.DoesNotExist:
            appointments = self.appointment_model.objects.filter(
                subject_identifier=self.subject_identifier).order_by('visit_code')
            self.selected_appointment = None
        context.update(
            appointments=appointments,
            selected_appointment=self.selected_appointment)
        return context


class DashboardMetaDataMixin:

    def get_context_data(self, **kwargs):
        context = super(DashboardMetaDataMixin, self).get_context_data(**kwargs)
        context.update(
            crfs=self.crfs,
            requisitions=self.requisitions)
        return context

    @property
    def crfs(self):
        crfs = []
        if self.selected_appointment:
            crf_meta_datas = CrfMetadata.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_code=self.selected_appointment.visit_code).order_by('show_order')
            for crf in crf_meta_datas:
                try:
                    obj = None
                    try:
                        options = {
                            '{}__appointment'.format(crf.model_class.visit_model_attr()): self.selected_appointment}
                    except AttributeError as e:
                        if 'visit_model_attr' not in str(e):
                            raise DashboardError(str(e))
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted a non-crf entry in crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                    obj = crf.model_class.objects.get(**options)
                    crf.instance = obj
                    crf.visit_attr_name = crf.model_class.visit_model_attr()
                    crf.visit = getattr(crf.instance, crf.visit_attr_name)
                    crf.url = obj.get_absolute_url()
                    crf.title = obj._meta.verbose_name
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
        if self.selected_appointment:
            requisition_meta_data = RequisitionMetadata.objects.filter(
                subject_identifier=self.subject_identifier, visit_code=self.selected_appointment.visit_code)
            for requisition in requisition_meta_data:
                try:
                    obj = None
                    options = {
                        '{}__appointment'.format(requisition.model_class.visit_model_attr()): self.selected_appointment,
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


class DashboardMixin(DashboardMetaDataMixin, DashboardAppointmentMixin, DashboardSubjectMixin):
    pass
