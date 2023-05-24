from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from django.db import models, transaction
from django.db.models.deletion import ProtectedError
from edc_visit_schedule import site_visit_schedules

if TYPE_CHECKING:
    from .models import Appointment


class AppointmentDeleteError(Exception):
    pass


class AppointmentManagerError(Exception):
    pass


class SubjectOnScheduleError(Exception):
    pass


class AppointmentManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(
        self,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ) -> Appointment:
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )

    @staticmethod
    def get_query_options(**kwargs) -> Dict[Any]:
        """Returns a dictionary or options.

        Dictionary is based on the appointment instance or everything
        else.
        """
        appointment = kwargs.get("appointment")
        schedule_name = kwargs.get("schedule_name")
        subject_identifier = kwargs.get("subject_identifier")
        visit_schedule_name = kwargs.get("visit_schedule_name")
        options: Dict[Any] = dict(visit_code_sequence=0)
        try:
            options.update(
                subject_identifier=appointment.subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
            )
        except AttributeError:
            options.update(subject_identifier=subject_identifier)
            try:
                visit_schedule_name, schedule_name = visit_schedule_name.split(".")
                options.update(
                    visit_schedule_name=visit_schedule_name, schedule_name=schedule_name
                )
            except ValueError:
                options.update(visit_schedule_name=visit_schedule_name)
            except AttributeError:
                pass
            if schedule_name and not visit_schedule_name:
                raise TypeError(
                    f"Expected visit_schedule_name for schedule_name "
                    f"'{schedule_name}'. Got {visit_schedule_name}"
                )
            elif schedule_name:
                options.update(schedule_name=schedule_name)
        return options

    @staticmethod
    def get_visit_code(action, schedule, **kwargs) -> str | None:
        """Updates the options dictionary with the next or previous
        visit code in the schedule.

        if both visit_code and appointment are in kwargs visit_code
        takes precedence over apppointment.visit_code
        """
        visit_code = kwargs.get("visit_code")
        if not visit_code:
            try:
                appointment = kwargs.get("appointment")
                visit_code = appointment.visit_code
            except AttributeError:
                pass
        if action == "next":
            visit = schedule.visits.next(visit_code)
        elif action == "previous":
            visit = schedule.visits.previous(visit_code)
        else:
            raise AppointmentManagerError(
                f"Unknown action. Expected one of [next, previous]. Got '{action}'."
            )
        try:
            visit_code = visit.code
        except AttributeError:
            visit_code = None
        return visit_code

    def first_appointment(self, **kwargs) -> Appointment | None:
        """Returns the first appointment instance for the given criteria.

        For visit_code_sequence=0.

        For example:
            first_appointment = (Appointment.objects.
                first_appointment(appointment=appointment))
        or:
            first_appointment = Appointment.objects.first_appointment(
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name)
        """
        options = self.get_query_options(**kwargs)
        try:
            first_appointment = self.filter(**options).order_by(
                "timepoint", "visit_code_sequence"
            )[0]
        except IndexError:
            first_appointment = None
        return first_appointment

    def last_appointment(self, **kwargs) -> Appointment | None:
        """Returns the last appointment relative to the criteria.

        For visit_code_sequence=0.
        """
        options = self.get_query_options(**kwargs)
        try:
            last_appointment = [
                obj
                for obj in self.filter(**options).order_by("timepoint", "visit_code_sequence")
            ][-1]
        except IndexError:
            last_appointment = None
        return last_appointment

    def next_appointment(self, **kwargs) -> Appointment | None:
        """Returns the next appointment relative to the criteria or
        None if there is no next.

        For visit_code_sequence=0.

        Next is the next visit in a schedule, so schedule_name is required.

        For example:
            next_appointment = (Appointment.objects.
                first_appointment(appointment=appointment))
        or:
            next_appointment = Appointment.objects.first_appointment(
                visit_code=visit_code, appointment=appointment)
        or:
            next_appointment = Appointment.objects.first_appointment(
                visit_code=visit_code,
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name)
        """
        options = self.get_query_options(**kwargs)
        schedule = site_visit_schedules.get_visit_schedule(
            options.get("visit_schedule_name")
        ).schedules.get(options.get("schedule_name"))
        options.update(visit_code=self.get_visit_code("next", schedule, **kwargs))
        try:
            next_appointment = self.filter(**options).order_by(
                "timepoint", "visit_code_sequence"
            )[0]
        except IndexError:
            next_appointment = None
        return next_appointment

    def previous_appointment(self, **kwargs) -> Appointment | None:
        """Returns the previous appointment relative to the criteria
        or None if there is no previous.

        For visit_code_sequence=0.
        """
        options = self.get_query_options(**kwargs)
        schedule = site_visit_schedules.get_visit_schedule(
            options.get("visit_schedule_name")
        ).schedules.get(options.get("schedule_name"))
        options.update(visit_code=self.get_visit_code("previous", schedule, **kwargs))
        try:
            previous_appointment = (
                self.filter(**options)
                .order_by("timepoint", "visit_code_sequence")
                .reverse()[0]
            )
        except IndexError:
            previous_appointment = None
        return previous_appointment

    def delete_for_subject_after_date(
        self,
        subject_identifier=None,
        cutoff_datetime=None,
        op=None,
        visit_schedule_name=None,
        schedule_name=None,
        is_offstudy=None,
    ) -> int:
        """Deletes appointments for a given subject_identifier with
        appt_datetime greater than `dt`.

        If a visit form exists for any appointment, a ProtectedError will
        be raised.
        """
        # validate "op"
        valid_ops = ["gt", "gte"]
        if op and op not in valid_ops:
            formatted = ", ".join(valid_ops)
            raise TypeError(f"Allowed lookup operators are {formatted}. Got {op}.")
        op = "gte" if op is None else op

        # prepare options
        options = {
            "subject_identifier": subject_identifier,
            f"appt_datetime__{op}": cutoff_datetime,
        }
        if not is_offstudy:
            try:
                visit_schedule_name, schedule_name = visit_schedule_name.split(".")
            except (ValueError, AttributeError):
                pass
            if not schedule_name or not visit_schedule_name:
                raise AppointmentManagerError(
                    f"Expected both the visit_schedule_name and schedule_name. "
                    f"Got schedule_name='{schedule_name}', "
                    f"visit_schedule_name='{visit_schedule_name}'"
                )
            options.update(dict(visit_schedule_name=visit_schedule_name))
            options.update(dict(schedule_name=schedule_name))

        # delete future appointments until the first with a
        # visit report
        deleted = 0
        appointments = self.filter(**options).order_by("timepoint", "visit_code_sequence")
        for appointment in appointments.reverse():
            try:
                with transaction.atomic():
                    appointment.delete()
                    deleted += 1
            except ProtectedError:
                break
            except AppointmentDeleteError:
                pass
        return deleted
