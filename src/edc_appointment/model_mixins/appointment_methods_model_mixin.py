from __future__ import annotations

from typing import Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from edc_facility import Facility
from edc_visit_tracking.model_mixins import VisitModelMixin
from edc_visit_tracking.stubs import SubjectVisitModelStub

from ..stubs import AppointmentModelStub, TAppointmentModelStub
from ..utils import get_next_appointment, get_previous_appointment


class AppointmentMethodsModelError(Exception):
    pass


class AppointmentMethodsModelMixin(models.Model):

    """Mixin of methods for the appointment model only"""

    @property
    def visit_label(self) -> str:
        return f"{self.visit_code}.{self.visit_code_sequence}"

    @property
    def related_visit(self: AppointmentModelStub) -> SubjectVisitModelStub:
        """Returns the related visit model instance, or None"""
        visit = None
        for f in self._meta.get_fields():
            if f.related_model:
                if issubclass(f.related_model, VisitModelMixin):
                    with transaction.atomic():
                        try:
                            visit = f.related_model.objects.get(appointment=self)
                        except ObjectDoesNotExist:
                            pass
        return visit

    @property
    def facility(self: AppointmentModelStub) -> Facility:
        """Returns the facility instance for this facility name"""
        app_config = django_apps.get_app_config("edc_facility")
        return app_config.get_facility(name=self.facility_name)

    @classmethod
    def related_visit_model_attr(cls: TAppointmentModelStub) -> str:
        fields = []
        for f in cls._meta.get_fields():
            if f.related_model:
                if issubclass(f.related_model, VisitModelMixin):
                    fields.append(f)
                    break
        if len(fields) > 1:
            raise AppointmentMethodsModelError(
                f"More than one field on Appointment is related field to a visit model. "
                f"Got {fields}."
            )
        elif len(fields) == 0:
            raise AppointmentMethodsModelError(
                f"{cls} has no related visit model. "
                f"Expected the related visit model to be an instance "
                "of `VisitModelMixin`."
            )
        else:
            related_visit_model_attr = fields[0].name
        return related_visit_model_attr

    @classmethod
    def visit_model_cls(cls: TAppointmentModelStub) -> Type[SubjectVisitModelStub]:
        return getattr(cls, cls.related_visit_model_attr()).related.related_model

    @property
    def next_by_timepoint(self: AppointmentModelStub) -> AppointmentModelStub | None:
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
    def last_visit_code_sequence(self: AppointmentModelStub) -> int | None:
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
    def next_visit_code_sequence(self: AppointmentModelStub) -> int:
        """Returns an integer that is the next visit_code_sequence.

        A sequence would be 1000.0, 1000.1, 1000.2, ...
        """
        if self.last_visit_code_sequence:
            return self.last_visit_code_sequence + 1
        return self.visit_code_sequence + 1

    def get_last_appointment_with_visit_report(
        self: AppointmentModelStub,
    ) -> AppointmentModelStub | None:
        """Returns the last appointment model instance,
        or None, with a completed visit report.

        Ordering is by appointment timepoint/visit_code_sequence
        with a completed visit report.
        """
        appointment = None
        visit = (
            self.__class__.visit_model_cls()
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
    def previous_by_timepoint(self: AppointmentModelStub) -> AppointmentModelStub | None:
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
    def previous(self: AppointmentModelStub) -> AppointmentModelStub | None:
        """Returns the previous appointment or None in this schedule
        for visit_code_sequence=0.
        """
        return get_previous_appointment(self, include_interim=False)

    @property
    def next(self: AppointmentModelStub) -> AppointmentModelStub | None:
        """Returns the next appointment or None in this schedule
        for visit_code_sequence=0.
        """
        return get_next_appointment(self, include_interim=False)

    @property
    def relative_previous(self: AppointmentModelStub) -> AppointmentModelStub | None:
        return get_previous_appointment(self, include_interim=True)

    @property
    def relative_next(self: AppointmentModelStub) -> AppointmentModelStub | None:
        return get_next_appointment(self, include_interim=True)

    class Meta:
        abstract = True
