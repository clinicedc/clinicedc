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

    dashboard_url = None
    base_html = 'edc_base/base.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSubjectMixin, self).get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get('subject_identifier')
        self.show = self.kwargs.get('show')
        context.update(
            dashboard_url=self.dashboard_url,
            base_html=self.base_html,
            subject_identifier=self.subject_identifier,
            show=self.show)
        return context


class DashboardAppointmentMixin:

    visit_model = None

    def appointment_next_url_parameters(self, obj, selected_obj=None, **extra_parameters):
        """Returns a dictionary of parameters needed to reverse the next_url."""
        attrs = ['subject_identifier'] + ['selected_appointment'] if selected_obj else []
        values = [obj.subject_identifier] + [str(selected_obj.id)] if selected_obj else []
        parameters = dict(zip(attrs, values))
        parameters.update(**extra_parameters)
        return parameters

    def appointment_next_url(self, obj, selected_obj=None, **extra_parameters):
        """Returns the next_url querystring segment."""
        parameters = ['='.join(z) for z in list(
            self.appointment_next_url_parameters(
                obj, selected_obj=selected_obj, **extra_parameters).items())]
        return '{},{}?'.format(
            self.dashboard_url, ','.join(parameters), parameters)

    def appointment_wrapper(self, obj, selected_obj=None, **extra_parameters):
        """Wraps the appointment objects.

        * extra_parameters will be added to the default dictionary of parameters needed
          to reverse the next_url."""
        try:
            obj.visit = self.visit_model.objects.get(appointment=obj)
        except self.visit_model.DoesNotExist:
            obj.visit = None
        obj.next_url = self.appointment_next_url(
            obj, selected_obj=selected_obj, **extra_parameters)
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
