from django.contrib.auth.mixins import LoginRequiredMixin
from edc_label.printers_mixin import PrintersMixin
from django.views.generic.edit import ProcessFormView
from django.urls.base import reverse
from django.http.response import HttpResponseRedirect
from django.conf import settings

from ..reports import ClinicManifestReport
from edc_lab.models.model_mixins.requisition.requisition_model_mixin import RequisitionModelMixin
from edc_appointment.models.appointment import Appointment


class PrintClinicManifestView(LoginRequiredMixin, PrintersMixin, ProcessFormView):

    success_url = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    def __init__(self, **kwargs):
        self._requisition_model_cls = None
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        subject_identifier = request.POST.get('subject_identifier')
        appointment_pk = request.POST.get('appointment')
        self.appointment = Appointment.objects.get(pk=appointment_pk)
        if request.POST.get('pdf'):
            response = self.print_manifest()
            return response
        success_url = reverse(self.success_url, kwargs=dict(
            subject_identifier=subject_identifier,
            appointment=appointment_pk))
        return HttpResponseRedirect(redirect_to=success_url)

    @property
    def requisition_model_cls(self):
        if not self._requisition_model_cls:
            for attr in dir(self.appointment.visit_model_cls):
                try:
                    self._requisition_model_cls = getattr(
                        getattr(self.appointment.visit_model_cls, attr), 'model')
                except AttributeError:
                    pass
                else:
                    if issubclass(self._requisition_model_cls, RequisitionModelMixin):
                        break
        return self._requisition_model_cls

    def print_manifest(self):
        related_visit_model_attr = self.requisition_model_cls.related_visit_model_attr()
        requisitions = self.requisition_model_cls.objects.filter(
            {related_visit_model_attr: self.appointment.visit})
        manifest_report = ClinicManifestReport(
            requisitions=requisitions, user=self.request.user)
        return manifest_report.render()
