from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from edc_appointment.constants import MISSED_APPT
from edc_appointment.utils import get_appointment_model_cls


class VisitsForSubjectView(View):
    """Return the subject's (non-missed) appointments as JSON.

    Populated from appointments so a reviewer can associate an order with a
    visit even when the SubjectVisit has not been reported yet. Each option's
    label carries the subject visit report date (as a date) when the visit
    has been reported, and nothing otherwise.

    Response format::

        {"visits": [{"value": "1000.0", "label": "1000.0 — 2026-03-11"}, ...]}
    """

    def get(
        self, request: object, *args: object, **kwargs: object  # noqa: ARG002
    ) -> JsonResponse:
        subject_identifier = request.GET.get("subject_identifier", "").strip()
        if not subject_identifier:
            return JsonResponse({"visits": []})

        subject_visit_model = apps.get_model(settings.SUBJECT_VISIT_MODEL)
        report_map = {
            (visit_code, visit_code_sequence or 0): report_datetime
            for visit_code, visit_code_sequence, report_datetime in (
                subject_visit_model.objects.filter(
                    subject_identifier=subject_identifier
                ).values_list("visit_code", "visit_code_sequence", "report_datetime")
            )
        }

        appointments = (
            get_appointment_model_cls()
            .objects.filter(subject_identifier=subject_identifier)
            .exclude(appt_timing=MISSED_APPT)
            .order_by("appt_datetime")
            .values_list("visit_code", "visit_code_sequence")
        )

        seen: set[tuple[str, int]] = set()
        visits = []
        for visit_code, visit_code_sequence in appointments:
            key = (visit_code, visit_code_sequence or 0)
            if key in seen:
                continue
            seen.add(key)
            value = f"{key[0]}.{key[1]}"
            report_datetime = report_map.get(key)
            label = (
                f"{value} — {report_datetime.date().isoformat()}"
                if report_datetime
                else value
            )
            visits.append({"value": value, "label": label})

        return JsonResponse({"visits": visits})
