from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_facility.facility import Facility
from edc_facility.utils import get_facility
from edc_visit_tracking.model_mixins import get_related_visit_model_attr

from ..utils import get_next_appointment, get_previous_appointment

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin

    from ..models import Appointment

    VisitModel = TypeVar("VisitModel", bound=VisitModelMixin)


class AppointmentMethodsModelError(Exception):
    pass


class AppointmentMethodsModelMixin(models.Model):

    """Mixin of methods for the appointment model only"""

    @property
    def facility(self: Appointment) -> Facility:
        """Returns the facility instance for this facility name"""
        return get_facility(name=self.facility_name)

    @property
    def visit_label(self: Appointment) -> str:
        return f"{self.visit_code}.{self.visit_code_sequence}"

    @property
    def related_visit(self: Appointment) -> VisitModel | None:
        """Returns the related visit model instance, or None"""
        related_visit = None
        try:
            related_visit = getattr(self, self.related_visit_model_attr())
        except ObjectDoesNotExist:
            pass
        except AttributeError:
            query = getattr(self, f"{self.related_visit_model_attr()}_set")
            if query:
                if qs := query.all():
                    related_visit = qs[0]
        return related_visit

    @classmethod
    def related_visit_model_attr(cls: Appointment) -> str:
        """Returns the reversed related visit attr"""
        return get_related_visit_model_attr(cls)

    @classmethod
    def related_visit_model_cls(cls: Appointment) -> VisitModel:
        return getattr(cls, cls.related_visit_model_attr()).related.related_model

    @property
    def next_by_timepoint(self: Appointment) -> Appointment | None:
        """Returns the next appointment or None of all appointments
        for this subject for visit_code_sequence=0.
        """
        return (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                timepoint__gt=self.timepoint,
                visit_code_sequence=0,
            )
            .order_by("timepoint")
            .first()
        )

    @property
    def last_visit_code_sequence(self: Appointment) -> int | None:
        """Returns an integer, or None, that is the visit_code_sequence
        of the last appointment for this visit code that is not self.
        (ordered by visit_code_sequence).

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        obj = (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence__gt=self.visit_code_sequence,
            )
            .order_by("visit_code_sequence")
            .last()
        )
        if obj:
            return obj.visit_code_sequence
        return None

    @property
    def next_visit_code_sequence(self: Appointment) -> int:
        """Returns an integer that is the next visit_code_sequence.

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        if self.last_visit_code_sequence:
            return self.last_visit_code_sequence + 1
        return self.visit_code_sequence + 1

    def get_last_appointment_with_visit_report(
        self: Appointment,
    ) -> Appointment | None:
        """Returns the last appointment model instance,
        or None, with a completed visit report.

        Ordering is by appointment timepoint/visit_code_sequence
        with a completed visit report.
        """
        appointment = None
        visit = (
            self.__class__.related_visit_model_cls()
            .objects.filter(
                appointment__subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            )
            .order_by("appointment__timepoint", "appointment__visit_code_sequence")
            .last()
        )
        if visit:
            appointment = visit.appointment
        return appointment

    @property
    def previous_by_timepoint(self: Appointment) -> Appointment | None:
        """Returns the previous appointment or None by timepoint
        for visit_code_sequence=0.
        """
        return (
            self.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                timepoint__lt=self.timepoint,
                visit_code_sequence=0,
            )
            .order_by("timepoint")
            .last()
        )

    @property
    def first(self: Appointment) -> Appointment:
        """Returns the first appointment for this timepoint."""
        if self.visit_code_sequence == 0:
            return self
        return self.__class__.objects.get(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            timepoint=self.timepoint,
            visit_code_sequence=0,
        )

    @property
    def previous(self: Appointment) -> Appointment | None:
        """Returns the previous appointment or None in this schedule
        for visit_code_sequence=0.
        """
        return get_previous_appointment(self, include_interim=False)

    @property
    def next(self: Appointment) -> Appointment | None:
        """Returns the next appointment or None in this schedule
        for visit_code_sequence=0.
        """
        return get_next_appointment(self, include_interim=False)

    @property
    def relative_previous(self: Appointment) -> Appointment | None:
        return get_previous_appointment(self, include_interim=True)

    @property
    def relative_next(self: Appointment) -> Appointment | None:
        return get_next_appointment(self, include_interim=True)

    class Meta:
        abstract = True
