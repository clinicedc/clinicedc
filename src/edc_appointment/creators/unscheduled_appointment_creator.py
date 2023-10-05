from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from dateutil.relativedelta import relativedelta
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError
from edc_utils import formatted_datetime, to_utc
from edc_utils.date import to_local
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.utils import get_lower_datetime

from ..constants import (
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
    UNSCHEDULED_APPT,
)
from ..exceptions import AppointmentPermissionsRequired, AppointmentWindowError
from .appointment_creator import AppointmentCreator, CreateAppointmentError

if TYPE_CHECKING:
    from edc_facility import Facility

    from ..models import Appointment


class UnscheduledAppointmentError(Exception):
    pass


class UnscheduledAppointmentNotAllowed(Exception):
    pass


class InvalidVisitCodeSequencesError(Exception):
    pass


class InvalidTimepointError(Exception):
    pass


class InvalidParentAppointmentStatusError(Exception):
    pass


class InvalidParentAppointmentMissingVisitError(Exception):
    pass


class AppointmentInProgressError(Exception):
    pass


class UnscheduledAppointmentCreator:

    """Attempts to create a new unscheduled appointment where the
    visit code sequence == the given `visit_code_sequence` or raises.
    """

    appointment_creator_cls = AppointmentCreator

    def __init__(
        self,
        subject_identifier: str = None,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        visit_code: str = None,
        suggested_visit_code_sequence: int = None,
        suggested_appt_datetime: datetime | None = None,
        facility: Facility = None,
        request: Any | None = None,
    ):
        self._parent_appointment = None
        self._calling_appointment = None
        self.appointment = None
        self._suggested_appt_datetime = suggested_appt_datetime
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.schedule_name = schedule_name
        self.visit_code = visit_code
        self.visit_code_sequence = suggested_visit_code_sequence
        if self.visit_code_sequence is None:
            raise InvalidVisitCodeSequencesError("visit code sequence cannot be None")
        if self.visit_code_sequence < 1:
            raise InvalidVisitCodeSequencesError(
                "suggested visit code sequence cannot be less than 1"
            )
        self.facility = facility
        self.visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        self.schedule = self.visit_schedule.schedules.get(schedule_name)
        self.appointment_model_cls = self.schedule.appointment_model_cls
        self.has_perm_or_raise(request)
        self.create_or_raise()

    def create_or_raise(self) -> None:
        visit = self.visit_schedule.schedules.get(self.schedule_name).visits.get(
            self.visit_code
        )
        if not visit:
            raise UnscheduledAppointmentError(
                "Invalid visit. Got None using {"
                f"visit_schedule_name='{self.visit_schedule_name}',"
                f"schedule_name='{self.schedule_name}',"
                f"visit_code='{self.visit_code}'" + "}"
            )
        elif not visit.allow_unscheduled:
            raise UnscheduledAppointmentNotAllowed(
                f"Not allowed. Visit {self.visit_code} is not configured for "
                "unscheduled appointments."
            )
        elif (
            self.parent_appointment
            and self.parent_appointment.next
            and to_utc(self.suggested_appt_datetime)
            >= get_lower_datetime(self.parent_appointment.next)
        ):
            dt = formatted_datetime(to_local(self.suggested_appt_datetime))
            next_dt = formatted_datetime(
                to_local(get_lower_datetime(self.parent_appointment.next))
            )
            raise UnscheduledAppointmentError(
                "Appointment date exceeds window period. Next appointment is "
                f"{self.parent_appointment.next.visit_code} and lower window starts "
                f"on {next_dt}. Got {dt}. Perhaps catch this in the form."
            )
        else:
            # do not allow new unscheduled if any appointments are IN_PROGRESS
            try:
                obj = self.appointment_model_cls.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    appt_status=IN_PROGRESS_APPT,
                )
            except MultipleObjectsReturned as e:
                raise UnscheduledAppointmentError(e)
            except ObjectDoesNotExist:
                pass
            else:
                raise AppointmentInProgressError(
                    f"Not allowed. Appointment {obj.visit_code}."
                    f"{obj.visit_code_sequence} is in progress."
                )
            try:
                appointment_creator = self.appointment_creator_cls(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=self.visit_schedule_name,
                    schedule_name=self.schedule_name,
                    visit=visit,
                    suggested_datetime=self.suggested_appt_datetime,
                    timepoint=self.parent_appointment.timepoint,
                    timepoint_datetime=self.parent_appointment.timepoint_datetime,
                    visit_code_sequence=self.parent_appointment.next_visit_code_sequence,
                    facility=self.facility,
                    appt_status=NEW_APPT,
                    appt_reason=UNSCHEDULED_APPT,
                    ignore_window_period=self.ignore_window_period,
                )
            except CreateAppointmentError:
                raise
            except IntegrityError as e:
                raise CreateAppointmentError(e)
            except AppointmentWindowError as e:
                msg = str(e).replace("Perhaps catch this in the form", "")
                raise UnscheduledAppointmentError(
                    f"Unable to create unscheduled appointment. {msg}"
                )
            self.appointment = appointment_creator.appointment

    def has_perm_or_raise(self, request) -> None:
        if request and not request.user.has_perm(
            f"{self.appointment_model_cls._meta.app_label}."
            f"add_{self.appointment_model_cls._meta.model_name}"
        ):
            raise AppointmentPermissionsRequired(
                "You do not have permission to create an appointment"
            )

    @property
    def ignore_window_period(self: Any) -> bool:
        value = False
        if (
            self.calling_appointment
            and self.calling_appointment.next
            and self.calling_appointment.next.appt_status in [INCOMPLETE_APPT, COMPLETE_APPT]
            and self.suggested_appt_datetime < self.calling_appointment.next.appt_datetime
        ):
            value = True
        return value

    @property
    def suggested_appt_datetime(self):
        if not self._suggested_appt_datetime:
            self._suggested_appt_datetime = (
                self.calling_appointment.appt_datetime + relativedelta(days=1)
            )
        return self._suggested_appt_datetime

    @property
    def calling_appointment(self) -> Appointment:
        """Returns the appointment which preceeds the to-be-created
        unscheduled appt.

        It must exist.

        Note: subtracting 1 from `visit_code_sequence` implies the
        visit_code_sequence cannot be less than 1.

        if visit_code_sequence = 1, calling_appointment and parent_appointment
        will be the same instance.
        """
        if not self._calling_appointment:
            opts = dict(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence=self.visit_code_sequence - 1,
                timepoint=self.parent_appointment.timepoint,
            )
            self._calling_appointment = self.appointment_model_cls.objects.get(**opts)
        return self._calling_appointment

    @property
    def parent_appointment(self) -> Appointment:
        """Returns the parent or 'scheduled' appointment
        (visit_code_sequence=0).
        """
        if not self._parent_appointment:
            options = dict(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence=0,
            )
            self._parent_appointment = self.appointment_model_cls.objects.get(**options)
            if not self._parent_appointment.related_visit:
                raise InvalidParentAppointmentMissingVisitError(
                    f"Unable to create unscheduled appointment. An unscheduled "
                    f"appointment cannot be created if the parent appointment "
                    f"visit form has not been completed. "
                    f"Got appointment '{self.visit_code}.0'."
                )
            else:
                if self._parent_appointment.appt_status not in [
                    COMPLETE_APPT,
                    INCOMPLETE_APPT,
                ]:
                    raise InvalidParentAppointmentStatusError(
                        f"Unable to create unscheduled appointment. An unscheduled "
                        f"appointment cannot be created if the parent appointment "
                        f"is 'new' or 'in progress'. Got appointment "
                        f"'{self.visit_code}' is "
                        f"{self._parent_appointment.get_appt_status_display().lower()}."
                    )

        return self._parent_appointment
