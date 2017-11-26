from django.apps import apps as django_apps
from edc_appointment.appointment_creator import AppointmentCreator
from edc_appointment.constants import COMPLETE_APPT, INCOMPLETE_APPT, NEW_APPT,\
    CANCELLED_APPT
from edc_base.utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from django.core.exceptions import ObjectDoesNotExist


class UnscheduledAppointmentError(Exception):
    pass


class UnscheduledAppointmentCreator:

    appointment_creator_cls = AppointmentCreator

    def __init__(self, subject_identifier=None,
                 visit_schedule_name=None, schedule_name=None, visit_code=None,
                 **kwargs):
        self._parent_appointment = None
        self.appointment = None
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.schedule_name = schedule_name
        self.visit_code = visit_code
        self.visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name)
        visit = self.visit_schedule.schedules.get(
            schedule_name).visits.get(visit_code)
        if visit.allow_unscheduled:
            # don't allow if next appointment is already started.
            next_by_timepoint = self.parent_appointment.next_by_timepoint
            if next_by_timepoint:
                if next_by_timepoint.appt_status not in [NEW_APPT, CANCELLED_APPT]:
                    raise UnscheduledAppointmentError(
                        f'Not allowed. Visit {next_by_timepoint.visit_code} has '
                        'already been started.')
            appointment_creator = self.appointment_creator_cls(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name, visit=visit,
                suggested_datetime=self.parent_appointment.appt_datetime,
                timepoint_datetime=self.parent_appointment.timepoint_datetime,
                visit_code_sequence=self.parent_appointment.next_visit_code_sequence)
            self.appointment = appointment_creator.appointment
        else:
            raise UnscheduledAppointmentError(
                f'Not allowed. Visit {visit_code} is not configured for '
                'unscheduled appointments.')

    @property
    def parent_appointment(self):
        if not self._parent_appointment:
            visit_model_cls = django_apps.get_model(
                self.visit_schedule.visit_model)
            options = dict(
                appointment__subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                appointment__appt_status__in=[COMPLETE_APPT, INCOMPLETE_APPT],
                visit_code=self.visit_code)
            try:
                self._parent_appointment = visit_model_cls.objects.get(
                    **options).appointment
            except ObjectDoesNotExist:
                raise UnscheduledAppointmentError(
                    f'Unable to create unscheduled appointment. An unscheduled '
                    f'appointment cannot be created if the parent appointment '
                    f'is \'new\' or \'in progress\'. Got appointment \'{self.visit_code}\' is '
                    f'\'{self._parent_appointment.get_appt_status_display().lower()}\'.')
        return self._parent_appointment
