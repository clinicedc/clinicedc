from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views.generic.edit import ProcessFormView
from edc_appointment.models.appointment import Appointment
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO
from edc_lab.models.model_mixins import RequisitionModelMixin
from edc_label.printers_mixin import PrintersMixin


class VerifyRequisitionLabelView(LoginRequiredMixin, PrintersMixin, ProcessFormView):

    success_url = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')

    def get_requisition(self, appointment_pk=None, requisition_identifier=None):
        requisition = None
        appointment = Appointment.objects.get(pk=appointment_pk)
        subject_visit = appointment.visit
        for attr in dir(subject_visit):
            try:
                model_cls = getattr(getattr(subject_visit, attr), 'model')
            except AttributeError:
                model_cls = None
            else:
                if issubclass(model_cls, (RequisitionModelMixin, )):
                    try:
                        requisition = getattr(subject_visit, attr).get(
                            requisition_identifier=requisition_identifier.strip())
                    except ObjectDoesNotExist:
                        pass
                    break
        return requisition

    def post(self, request, *args, **kwargs):
        alert = 1
        error = 1
        subject_identifier = request.POST.get('subject_identifier')
        appointment_pk = request.POST.get('appointment')
        requisition_identifier = request.POST.get('requisition_identifier')
        if requisition_identifier:
            requisition_identifier = requisition_identifier.replace(
                '-', '').replace(' ', '')
            requisition = self.get_requisition(
                appointment_pk=appointment_pk,
                requisition_identifier=requisition_identifier)
            if requisition and requisition.is_drawn != NO:
                alert = None
                error = 0
                requisition.clinic_verified = YES
                requisition.clinic_verified_datetime = get_utcnow()
                requisition.is_drawn = requisition.is_drawn or YES
                requisition.drawn_datetime = requisition.drawn_datetime or get_utcnow()
                requisition.save()
        success_url = reverse(self.success_url, kwargs=dict(
            subject_identifier=subject_identifier,
            appointment=appointment_pk,
            scanning=1,
            error=error))
        return HttpResponseRedirect(
            redirect_to=f'{success_url}?alert={alert}#verify_requisition_identifier')
