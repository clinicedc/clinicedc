from django.apps import apps as django_apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import ProcessFormView
from django.contrib import messages
from django.urls.base import reverse
from django.http.response import HttpResponseRedirect
from django.conf import settings
from edc_label.job_result import JobResult
from edc_label.printers_mixin import PrintersMixin
from edc_metadata.models import RequisitionMetadata
from edc_appointment.models.appointment import Appointment
from edc_metadata.constants import REQUIRED, KEYED
from edc_lab.labels import RequisitionLabel
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import NO, YES
from edc_lab.models.model_mixins.requisition.requisition_model_mixin import RequisitionModelMixin
from ..reports import RequisitionReport
from edc_lab.models.manifest.consignee import Consignee


class RequisitionLabels:

    label_cls = RequisitionLabel
    label_template_name = 'requisition'

    def __init__(self, requisition_metadata=None, panel_names=None,
                 appointment=None, user=None):
        zpl_datas = []
        self.appointment = appointment
        for metadata in requisition_metadata.filter(
                panel_name__in=panel_names):
            panel = [
                r for r in appointment.visit.visit.all_requisitions
                if r.panel.name == metadata.panel_name][0].panel
            requisition = self.get_or_create_requisition(
                panel=panel, user=user)
            if requisition.is_drawn != NO:
                item_count = requisition.item_count or 1
                for item in range(1, item_count + 1):
                    label = self.label_cls(
                        requisition=requisition, user=user, item=item)
                    zpl_datas.append(label.render_as_zpl_data(copies=1))
        self.zpl_data = b''.join(zpl_datas)

    def get_or_create_requisition(self, panel=None, user=None):
        """Gets or creates a requisition.

        If created, the requisition created is incomplete; that is,
        is_drawn and drawn_datetime are None.
        """
        requisition_model_cls = django_apps.get_model(panel.requisition_model)
        visit_model_attr = requisition_model_cls.visit_model_attr()
        try:
            requisition_model_obj = requisition_model_cls.objects.get(
                panel=panel.panel_model_obj,
                **{f'{visit_model_attr}__appointment': self.appointment})
        except ObjectDoesNotExist:
            requisition_model_obj = requisition_model_cls(
                user_created=user.username,
                panel=panel.panel_model_obj,
                **{visit_model_attr: self.appointment.visit})
            requisition_model_obj.get_requisition_identifier()
            requisition_model_obj.save()
        return requisition_model_obj


class RequisitionPrintActionsView(LoginRequiredMixin, PrintersMixin, ProcessFormView):

    job_result_cls = JobResult
    requisition_report_cls = RequisitionReport
    requisition_labels_cls = RequisitionLabels
    success_url = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    print_selected_button = 'print_selected_labels'
    print_all_button = 'print_all_labels'
    print_requisition = 'print_requisition'
    checkbox_name = 'selected_panel_names'

    def __init__(self, **kwargs):
        self._appointment = None
        self._selected_panel_names = []
        self._requisition_metadata = None
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):

        print(self.request.POST.get('submit'))
        print(self.selected_panel_names)

        if self.selected_panel_names:

            if self.request.POST.get('submit') in [self.print_all_button, self.print_selected_button]:
                self.print_labels_action()
            elif self.request.POST.get('submit_print_requisition'):
                self.consignee = Consignee.objects.get(
                    pk=self.request.POST.get('submit_print_requisition'))
                response = self.render_manifest_to_response_action()
                return response

        subject_identifier = request.POST.get('subject_identifier')
        success_url = reverse(self.success_url, kwargs=dict(
            subject_identifier=subject_identifier,
            appointment=str(self.appointment.pk)))
        return HttpResponseRedirect(redirect_to=f'{success_url}')

    def print_labels_action(self):
        labels = self.requisition_labels_cls(
            requisition_metadata=self.requisition_metadata.filter(
                panel_name__in=self.selected_panel_names),
            panel_names=self.selected_panel_names,
            appointment=self.appointment,
            user=self.request.user)

        job_id = self.clinic_label_printer.stream_print(
            zpl_data=labels.zpl_data)
        job_result = self.job_result_cls(
            name=labels.label_template_name, copies=1, job_ids=[job_id],
            printer=self.clinic_label_printer)
        messages.success(self.request, job_result.message)

    def render_manifest_to_response_action(self):
        requisition_report = self.requisition_report_cls(
            appointment=self.appointment,
            selected_panel_names=self.selected_panel_names,
            consignee=self.consignee,
            request=self.request)
        return requisition_report.render()

    @property
    def requisition_metadata(self):
        """Returns a queryset of keyed or required RequisitionMetadata for this
        appointment.
        """
        if not self._requisition_metadata:
            appointment = Appointment.objects.get(
                pk=self.request.POST.get('appointment'))
            subject_identifier = self.request.POST.get('subject_identifier')
            opts = dict(
                subject_identifier=subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence)
            self._requisition_metadata = RequisitionMetadata.objects.filter(
                entry_status__in=[KEYED, REQUIRED], **opts)
        return self._requisition_metadata

    @property
    def selected_panel_names(self):
        """Returns a list of panel names selected on the page.

        Returns all on the page if "print all" is submitted.
        """
        if not self._selected_panel_names:
            if self.request.POST.get('submit') == self.print_all_button:
                for metadata in self.requisition_metadata:
                    self._selected_panel_names.append(metadata.panel_name)
            else:
                self._selected_panel_names = self.request.POST.getlist(
                    self.checkbox_name) or []
        return self._selected_panel_names

    @property
    def appointment(self):
        if not self._appointment:
            self._appointment = Appointment.objects.get(
                pk=self.request.POST.get('appointment'))
        return self._appointment

    @property
    def verified_requisitions(self):
        """Returns a list of requisition model instances related
        to this appointment.
        """
        verified_requisitions = []
        for k, v in self.appointment.visit_model_cls().__dict__.items():
            try:
                model_cls = getattr(getattr(v, 'rel'), 'related_model')
            except AttributeError:
                pass
            else:
                if issubclass(model_cls, RequisitionModelMixin):
                    verified_requisitions.extend(
                        list(getattr(self.appointment.visit, k).filter(clinic_verified=YES)))
        return verified_requisitions
