from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from edc_appointment.constants import MISSED_APPT


class VisitsForSubjectView(View):
    """Return non-missed visits for a subject as JSON.

    Response format::

        {"visits": [{"value": "1000.0", "label": "1000.0"}, ...]}
    """

    def get(
        self, request: object, *args: object, **kwargs: object  # noqa: ARG002
    ) -> JsonResponse:
        subject_identifier = request.GET.get("subject_identifier", "").strip()
        if not subject_identifier:
            return JsonResponse({"visits": []})

        subject_visit_model = apps.get_model(settings.SUBJECT_VISIT_MODEL)
        qs = (
            subject_visit_model.objects.filter(
                subject_identifier=subject_identifier,
            )
            .exclude(appointment__appt_timing=MISSED_APPT)
            .values_list("visit_code", "visit_code_sequence")
            .distinct()
            .order_by("visit_code", "visit_code_sequence")
        )

        visits = []
        for visit_code, visit_code_sequence in qs:
            seq = visit_code_sequence or 0
            value = f"{visit_code}.{seq}"
            visits.append({"value": value, "label": value})

        return JsonResponse({"visits": visits})
