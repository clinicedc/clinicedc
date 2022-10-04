from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Union

from edc_visit_tracking.constants import UNSCHEDULED

from ..constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from ..creators import UnscheduledAppointmentCreator
from ..models import Appointment


class AppointmentTestCaseMixin:
    def get_timepoint_from_visit_code(
        self: Any,
        instance: Any,
        visit_code: str,
    ) -> Optional[Union[float, Decimal]]:
        timepoint = None
        for v in instance.schedule.visits.timepoints:
            if v.name == visit_code:
                timepoint = v.timepoint
                break
        return timepoint

    def get_appointment(
        self,
        subject_identifier: Optional[str] = None,
        visit_code: Optional[str] = None,
        visit_code_sequence: Optional[int] = None,
        reason: Optional[str] = None,
        appt_datetime: Optional[datetime] = None,
        timepoint: Optional[Union[float, Decimal]] = None,
    ):
        if timepoint is not None:
            appointment = Appointment.objects.get(
                subject_identifier=subject_identifier,
                timepoint=timepoint,
                visit_code_sequence=visit_code_sequence,
            )
        else:
            appointment = Appointment.objects.get(
                subject_identifier=subject_identifier,
                visit_code=visit_code,
                visit_code_sequence=visit_code_sequence,
            )
        if appt_datetime:
            appointment.appt_datetime = appt_datetime
            appointment.save()
            appointment.refresh_from_db()
        if reason == UNSCHEDULED:
            appointment = self.create_unscheduled_appointment(appointment)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()
        return appointment

    @staticmethod
    def create_unscheduled_appointment(appointment):
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        appt_creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence + 1,
            timepoint=appointment.timepoint,
            facility=appointment.facility,
        )
        return appt_creator.appointment
