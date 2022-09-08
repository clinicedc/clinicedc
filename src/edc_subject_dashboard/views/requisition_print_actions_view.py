from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from edc_appointment.models import Appointment
from edc_constants.constants import YES
from edc_lab.model_mixins import RequisitionModelMixin
from edc_lab.models import Consignee
from edc_label.job_result import JobResult
from edc_label.printers_mixin import PrinterError, PrintServerError
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.models import RequisitionMetadata

from ..requisition_labels import RequisitionLabels
from ..requisition_report import RequisitionReport
from .base_requisition_view import BaseRequisitionView


class RequisitionPrintActionsView(BaseRequisitionView):

    job_result_cls = JobResult
    requisition_report_cls = RequisitionReport
    requisition_labels_cls = RequisitionLabels
    print_selected_button = "print_selected_labels"
    print_all_button = "print_all_labels"
    print_requisition = "print_requisition"
    checkbox_name = "selected_panel_names"

    def __init__(self, **kwargs):
        self._appointment = None
        self._selected_panel_names = []
        self._requisition_metadata = None
        self._requisition_model_cls = None
        self.consignee = None
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = None
        if self.selected_panel_names:
            if self.request.POST.get("submit") in [
                self.print_all_button,
                self.print_selected_button,
            ]:
                self.print_labels_action()
            elif self.request.POST.get("submit_print_requisition"):
                self.consignee = Consignee.objects.get(
                    pk=self.request.POST.get("submit_print_requisition")
                )
                response = self.render_manifest_to_response_action()
        if not response:
            subject_identifier = request.POST.get("subject_identifier")
            success_url = reverse(
                self.get_success_url(),
                kwargs=dict(
                    subject_identifier=subject_identifier,
                    appointment=str(self.appointment.pk),
                ),
            )
            response = HttpResponseRedirect(redirect_to=f"{success_url}")
        return response

    def print_labels_action(self):
        labels = self.requisition_labels_cls(
            requisition_metadata=self.requisition_metadata.filter(
                panel_name__in=self.selected_panel_names
            ),
            panel_names=self.selected_panel_names,
            appointment=self.appointment,
            user=self.request.user,
        )

        if labels.zpl_data:
            try:
                job_id = self.clinic_label_printer.stream_print(zpl_data=labels.zpl_data)
            except (PrintServerError, PrinterError) as e:
                messages.error(self.request, str(e))
            else:
                job_result = self.job_result_cls(
                    name=labels.label_template_name,
                    copies=1,
                    job_ids=[job_id],
                    printer=self.clinic_label_printer,
                )
                messages.success(self.request, job_result.message)
        if labels.requisitions_not_printed:
            panels = ", ".join([str(r.panel_object) for r in labels.requisitions_not_printed])
            messages.warning(
                self.request, f"Some selected labels were not printed. See {panels}."
            )

    def render_manifest_to_response_action(self):
        panel_names = [r.panel.name for r in self.verified_requisitions]
        if panel_names:
            requisition_report = self.requisition_report_cls(
                appointment=self.appointment,
                selected_panel_names=panel_names,
                consignee=self.consignee,
                request=self.request,
            )
            response = requisition_report.render()
        else:
            messages.error(self.request, 'Nothing to do. No "verified" requisitions selected.')
            response = None
        return response

    @property
    def requisition_metadata(self):
        """Returns a queryset of keyed or required RequisitionMetadata for this
        appointment.
        """
        if not self._requisition_metadata:
            appointment = Appointment.objects.get(pk=self.request.POST.get("appointment"))
            subject_identifier = self.request.POST.get("subject_identifier")
            opts = dict(
                subject_identifier=subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence,
            )
            self._requisition_metadata = RequisitionMetadata.objects.filter(
                entry_status__in=[KEYED, REQUIRED], **opts
            )
        return self._requisition_metadata

    @property
    def selected_panel_names(self):
        """Returns a list of panel names selected on the page.

        Returns all on the page if "print all" is submitted.
        """
        if not self._selected_panel_names:
            if self.request.POST.get("submit") == self.print_all_button:
                for metadata in self.requisition_metadata:
                    self._selected_panel_names.append(metadata.panel_name)
            else:
                self._selected_panel_names = (
                    self.request.POST.getlist(self.checkbox_name) or []
                )
        return self._selected_panel_names

    @property
    def appointment(self):
        if not self._appointment:
            self._appointment = Appointment.objects.get(
                pk=self.request.POST.get("appointment")
            )
        return self._appointment

    @property
    def requisition_model_cls(self):
        if not self._requisition_model_cls:
            for v in self.appointment.visit_model_cls().__dict__.values():
                try:
                    model_cls = getattr(getattr(v, "rel"), "related_model")
                except AttributeError:
                    pass
                else:
                    if issubclass(model_cls, RequisitionModelMixin):
                        self._requisition_model_cls = model_cls
        return self._requisition_model_cls

    @property
    def verified_requisitions(self):
        """Returns a list of "verified" requisition model instances related
        to this appointment.
        """
        verified_requisitions = []
        for k, v in self.appointment.visit_model_cls().__dict__.items():
            try:
                model_cls = getattr(getattr(v, "rel"), "related_model")
            except AttributeError:
                pass
            else:
                if issubclass(model_cls, RequisitionModelMixin):
                    verified_requisitions.extend(
                        list(
                            getattr(self.appointment.related_visit, k).filter(
                                clinic_verified=YES,
                                panel__name__in=self.selected_panel_names,
                            )
                        )
                    )
        return verified_requisitions
