from __future__ import annotations

from typing import TYPE_CHECKING


class VisitSequenceError(Exception):
    pass


if TYPE_CHECKING:
    from edc_appointment.models import Appointment

    from edc_visit_tracking.model_mixins import VisitModelMixin


class VisitSequence:

    """A class that calculates the previous_visit and can enforce
    that visits are filled in sequence.
    """

    def __init__(self, appointment: Appointment, skip_enforce: bool | None = None) -> None:
        self._previous_appointment = None
        self.appointment = appointment
        self.skip_enforce = skip_enforce  # for tests
        self.appointment_model_cls = self.appointment.__class__
        descriptor = getattr(
            self.appointment_model_cls,
            self.appointment_model_cls.related_visit_model_attr(),
        )
        try:
            self.model_cls = descriptor.related.related_model
        except AttributeError:
            self.model_cls = descriptor.rel.related_model
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.visit_code = self.appointment.visit_code
        self.visit_code_sequence = self.appointment.visit_code_sequence

    def enforce_sequence(self) -> None:
        """Raises an exception if sequence is not adhered to; that is,
        the visit reports are not completed in order.
        """
        opts = dict(
            subject_identifier=self.appointment.subject_identifier,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            appt_datetime__lt=self.appointment.appt_datetime,
        )
        opts.update({f"{self.appointment.related_visit_model_attr()}__isnull": True})
        if appointments := self.appointment.__class__.objects.filter(**opts).order_by(
            "timepoint", "visit_code_sequence"
        ):
            msg = (
                "Previous visit report required. Enter report for "
                f"'{appointments.first().visit_code}."
                f"{appointments.first().visit_code_sequence}' "
                f"before completing this report."
            )
            raise VisitSequenceError(msg)

    @property
    def previous_visit_code(self) -> str:
        """Return the previous visit code or the existing
        visit code if sequence is not 0.
        """
        previous_visit_code = None
        if self.visit_code_sequence != 0:
            previous_visit_code = self.visit_code
        else:
            previous = self.appointment.schedule.visits.previous(self.visit_code)
            try:
                previous_visit_code = previous.code
            except AttributeError:
                pass
        return previous_visit_code

    @property
    def previous_appointment(self) -> Appointment | None:
        """Returns the previous appointment model instance or None.

        Considers interim appointments (relative_previous).
        """
        if not self._previous_appointment:
            if not self.skip_enforce:
                self.enforce_sequence()
            self._previous_appointment = self.appointment.relative_previous
        return self._previous_appointment

    @property
    def previous_visit(self) -> VisitModelMixin | None:
        """Returns the previous visit model instance if it exists
        or raises.

        A previous visit report must exist.
        """
        if self.previous_appointment:
            return self.model_cls.objects.get(appointment=self.previous_appointment)
        return None

    def get_previous_visit(self) -> VisitModelMixin | None:
        """Returns the previous visit model instance if it exists"""
        return self.previous_visit
