from django.apps import apps as django_apps
from django.urls.base import reverse

from edc_metadata.models import CrfMetadata, RequisitionMetadata


class DashboardSubjectMixin:

    dashboard_url_name = None

    def get_context_data(self, **kwargs):
        context = super(DashboardSubjectMixin, self).get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get('subject_identifier')
        self.show = self.kwargs.get('show')
        context.update(
            subject_identifier=self.subject_identifier,
            show=self.show,
            dashboard_url_name=self.dashboard_url_name)
        return context

    @property
    def dashboard_url(self):
        try:
            dashboard_url = reverse(
                self.dashboard_url_name,
                kwargs=dict(subject_identifier=self.subject_identifier))
        except AttributeError:
            dashboard_url = None
        return dashboard_url


class DashboardAppointmentMixin:

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').model

    def get_context_data(self, **kwargs):
        context = super(DashboardAppointmentMixin, self).get_context_data(**kwargs)
        appointment_pk = self.kwargs.get('appointment_pk')
        try:
            self.selected_appointment = self.appointment_model.objects.get(pk=appointment_pk)
            appointments = []
        except self.appointment_model.DoesNotExist:
            appointments = self.appointment_model.objects.filter(
                subject_identifier=self.subject_identifier).order_by('visit_code')
            self.selected_appointment = None
        context.update(
            appointments=appointments,
            selected_appointment=self.selected_appointment,
            appointment_pk=appointment_pk)
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
                    if self.dashboard == 'td_maternal':
                        obj = crf.model_class.objects.get(
                            maternal_visit__appointment=self.selected_appointment)
                    else:
                        obj = crf.model_class.objects.get(
                            infant_visit__appointment=self.selected_appointment)
                    crf.instance = obj
                    crf.url = obj.get_absolute_url()
                    crf.title = obj._meta.verbose_name
                except crf.model_class.DoesNotExist:
                    crf.instance = None
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
                    if self.dashboard == 'td_maternal':
                        obj = requisition.model_class.objects.get(
                            maternal_visit__appointment=self.selected_appointment, panel_name=requisition.panel_name)
                    else:
                        obj = requisition.model_class.objects.get(
                            infant_visit__appointment=self.selected_appointment, panel_name=requisition.panel_name)
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
