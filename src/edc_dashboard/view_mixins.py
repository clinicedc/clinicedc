import sys

from django.core.management.color import color_style
from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError
from django.apps import apps as django_apps
from django.urls.base import reverse

from edc_metadata.models import CrfMetadata, RequisitionMetadata

style = color_style()


class DashboardError(Exception):
    pass


class DashboardSubjectMixin:

    subject_dashboard_url_name = None
    subject_dashboard_base_html = 'edc_base/base.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSubjectMixin, self).get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get('subject_identifier')
        self.show = self.kwargs.get('show')
        context.update(
            subject_dashboard_base_html=self.subject_dashboard_base_html,
            subject_identifier=self.subject_identifier,
            show=self.show,
            subject_dashboard_url_name=self.subject_dashboard_url_name)
        return context


class DashboardAppointmentMixin:

    visit_model = None

    def appointment_wrapper(self, obj):
        try:
            obj.visit = self.visit_model.objects.get(appointment=obj)
        except self.visit_model.DoesNotExist:
            obj.visit = None
        return obj

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').model

    def get_context_data(self, **kwargs):
        context = super(DashboardAppointmentMixin, self).get_context_data(**kwargs)
        pk = self.kwargs.get('selected_appointment')
        appointments = []
        try:
            self.selected_appointment = self.appointment_wrapper(
                self.appointment_model.objects.get(pk=pk))
        except self.appointment_model.DoesNotExist:
            for obj in self.appointment_model.objects.filter(
                    subject_identifier=self.subject_identifier).order_by('visit_code'):
                appointments.append(self.appointment_wrapper(obj))
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
                            'Dashboard detected and deleted a non-crf entry in crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                    except LookupError as e:
                        # getting here means you changed a table name
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted an invalid crf entry in crf metadata. Got {}'.format(crf)))
                        sys.stdout.flush()
                    except OperationalError as e:
                        # getting here means you changed a table name but havent migrated the change
                        options = {}
                        crf.delete()
                        sys.stdout.write(style.NOTICE(
                            'Dashboard detected and deleted an invalid crf model name entry in crf metadata. '
                            'Got {}'.format(crf)))
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
