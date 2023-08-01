from __future__ import annotations

from edc_appointment.tests.test_case_mixins import AppointmentTestCaseMixin
from edc_consent.tests.test_case_mixins import ConsentTestCaseMixin
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls


class VisitTrackingTestCaseMixin(AppointmentTestCaseMixin, ConsentTestCaseMixin):
    def get_subject_visit(
        self,
        visit_code=None,
        visit_code_sequence=None,
        reason=None,
        appt_datetime=None,
    ):
        subject_visit_model_cls = get_related_visit_model_cls()
        reason = reason or SCHEDULED
        subject_consent = self.get_subject_consent()
        options = dict(
            subject_identifier=subject_consent.subject_identifier,
            visit_code=visit_code or DAY1,
            visit_code_sequence=(
                visit_code_sequence if visit_code_sequence is not None else 0
            ),
            reason=reason,
        )
        if appt_datetime:
            options.update(appt_datetime=appt_datetime)
        appointment = self.get_appointment(**options)
        subject_visit = subject_visit_model_cls(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.appt_datetime,
        )
        subject_visit.save()
        subject_visit.refresh_from_db()
        return subject_visit
