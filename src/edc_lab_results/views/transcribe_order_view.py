from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from edc_dashboard.view_mixins import EdcViewMixin

from ..models import Result
from ..transcribe import transcribe_results


class TranscribeOrderView(EdcViewMixin, View):
    """POST-only view to transcribe an order's results onto CRFs."""

    def post(self, request: object, *args: object, **kwargs: object) -> object:  # noqa: ARG002
        order_no = kwargs["order_no"]
        results_qs = Result.objects.filter(order_no=order_no)

        if not results_qs.exists():
            messages.error(request, f"No results found for order {order_no}.")
            return HttpResponseRedirect(
                reverse("edc_lab_results:order-detail", kwargs={"order_no": order_no})
            )

        summary = transcribe_results(results_qs)

        parts = []
        if summary.transcribed:
            parts.append(f"{summary.transcribed} transcribed")
        if summary.crf_created:
            parts.append(f"{summary.crf_created} CRF(s) created")
        if summary.already_correct:
            parts.append(f"{summary.already_correct} already correct")
        if summary.discrepancies:
            parts.append(f"{summary.discrepancies} discrepancies (not overwritten)")
        if summary.no_requisition:
            parts.append(f"{summary.no_requisition} panel(s) without requisition")
        if summary.no_visit:
            parts.append(f"{summary.no_visit} visit(s) not found")
        if summary.skipped:
            parts.append(f"{summary.skipped} skipped")

        msg = f"Transcription for order {order_no}: {', '.join(parts)}."

        if summary.discrepancies:
            messages.warning(request, msg)
        elif summary.transcribed or summary.crf_created:
            messages.success(request, msg)
        else:
            messages.info(request, msg)

        return HttpResponseRedirect(
            reverse("edc_lab_results:order-detail", kwargs={"order_no": order_no})
        )
