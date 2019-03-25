from django.http.response import HttpResponseRedirect
from django.urls.base import reverse

from ..requisition_verifier import RequisitionVerifier
from .base_requisition_view import BaseRequisitionView


class RequisitionVerifyActionsView(BaseRequisitionView):

    requisition_verifier_cls = RequisitionVerifier

    def post(self, request, *args, **kwargs):
        alert = 1
        error = 1
        subject_identifier = request.POST.get("subject_identifier")
        appointment_pk = request.POST.get("appointment")
        if request.POST.get("requisition_identifier"):
            requisition_identifier = (
                request.POST.get("requisition_identifier")
                .replace("-", "")
                .replace(" ", "")
            )
            requisition_verifier = self.requisition_verifier_cls(
                appointment_pk=appointment_pk,
                requisition_identifier=requisition_identifier,
            )
            if requisition_verifier.verified:
                alert = ""
                error = 0

        success_url = reverse(
            self.get_success_url(),
            kwargs=dict(
                subject_identifier=subject_identifier,
                appointment=appointment_pk,
                scanning=1,
                error=error,
            ),
        )
        return HttpResponseRedirect(
            redirect_to=f"{success_url}?alert={alert}#verify_requisition_identifier"
        )
