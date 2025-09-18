from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from edc_visit_schedule.models import VisitSchedule

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectVisitViewMixinError(Exception):
    pass


class SubjectVisitViewMixin:
    """Mixin to add the subject visit instance to the view.

    Declare together with the edc_appointment.AppointmentViewMixin.
    """

    def __init__(self, **kwargs):
        self._related_visit = None
        self._report_datetime = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        visit_schedule_pk = (
            "" if not self.get_visit_schedule() else str(self.get_visit_schedule().id)
        )
        kwargs.update(
            related_visit=self.related_visit,
            visit_schedule_model_obj=self.get_visit_schedule(),
            visit_schedule_pk=visit_schedule_pk,
        )
        return super().get_context_data(**kwargs)

    @property
    def related_visit(self) -> VisitModelMixin | None:
        if not self._related_visit:
            self.has_appointment_attr_or_raise()
            if self.appointment:
                try:
                    self._related_visit = self.appointment.related_visit
                except AttributeError as e:
                    raise SubjectVisitViewMixinError(
                        f"Visit model must have a OneToOne relation to appointment. Got {e}"
                    ) from e
        return self._related_visit

    def get_visit_schedule(self) -> VisitSchedule | None:
        """Returns the VisitSchedule model instance."""
        self.has_appointment_attr_or_raise()
        visit_schedule = None
        if self.appointment:
            opts = dict(
                visit_schedule_name=self.appointment.visit_schedule_name,
                schedule_name=self.appointment.schedule_name,
                visit_code=self.appointment.visit_code,
            )
            with contextlib.suppress(ObjectDoesNotExist):
                visit_schedule = VisitSchedule.objects.get(**opts)
        return visit_schedule

    @property
    def report_datetime(self):
        """Returns the report datetime in UTC"""
        if not self._report_datetime:
            try:
                self._report_datetime = self.related_visit.report_datetime
            except AttributeError:
                try:
                    self._report_datetime = self.appointment.appt_datetime
                except AttributeError:
                    self._report_datetime = timezone.now()
        return self._report_datetime

    def has_appointment_attr_or_raise(self) -> None:
        """Checks for 'appointment' attribute. If missing, assume you
        did not declare this view with AppointmentViewMixin.
        """
        try:
            self.appointment
        except AttributeError as e:
            if "appointment" in str(e):
                raise SubjectVisitViewMixinError(
                    f"Mixin must be declared together with AppointmentViewMixin. Got {e}"
                ) from e
            raise
