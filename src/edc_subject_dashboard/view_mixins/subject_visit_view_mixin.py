from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_utcnow
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            related_visit=self.related_visit,
            visit_schedule_pk=self.get_visit_schedule_pk(),
        )
        return context

    @property
    def related_visit(self) -> VisitModelMixin | None:
        if not self._related_visit:
            try:
                appointment = self.appointment
            except AttributeError as e:
                raise SubjectVisitViewMixinError(
                    f"Mixin must be declared together with AppointmentViewMixin. Got {e}"
                )
            else:
                if appointment:
                    try:
                        self._related_visit = appointment.related_visit
                    except AttributeError as e:
                        raise SubjectVisitViewMixinError(
                            "Visit model must have a OneToOne relation to appointment. "
                            f"Got {e}"
                        )
        return self._related_visit

    def get_visit_schedule_pk(self) -> str | None:
        """Returns a str(pk) from the VisitSchedule model."""
        visit_schedule_pk = None
        if self.appointment:
            opts = dict(
                visit_schedule_name=self.appointment.visit_schedule_name,
                schedule_name=self.appointment.schedule_name,
                visit_code=self.appointment.visit_code,
            )
            try:
                obj = VisitSchedule.objects.get(**opts)
            except ObjectDoesNotExist:
                pass
            else:
                visit_schedule_pk = str(obj.pk)
        return visit_schedule_pk

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
                    self._report_datetime = get_utcnow()
        return self._report_datetime
