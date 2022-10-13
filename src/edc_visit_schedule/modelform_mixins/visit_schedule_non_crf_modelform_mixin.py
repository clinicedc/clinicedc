from __future__ import annotations

from django import forms

from .. import site_visit_schedules
from ..schedule import Schedule
from ..site_visit_schedules import SiteVisitScheduleError
from ..subject_schedule import (
    NotOnScheduleError,
    NotOnScheduleForDateError,
    SubjectSchedule,
)
from ..utils import report_datetime_within_onschedule_offschedule_datetimes
from ..visit_schedule import VisitSchedule


class VisitScheduleNonCrfModelFormMixinError(Exception):
    pass


class VisitScheduleNonCrfModelFormMixin:
    """A ModelForm mixin for non-CRFs to validate that the subject is
    onschedule at the time of the report.
    """

    # loss_to_followup_model, offschedule_model, onschedule_model
    get_by_model_attr: str | None = None

    def clean(self):
        cleaned_data = super().clean()
        self.is_onschedule_or_raise()
        self.report_datetime_within_schedule_datetimes()
        return cleaned_data

    @property
    def visit_schedule_name(self) -> str:
        return self.visit_schedule.name

    @property
    def schedule_name(self) -> str:
        return self.schedule.name

    @property
    def visit_schedule(self) -> VisitSchedule:
        visit_schedule = getattr(self.instance, "visit_schedule", None)
        if not visit_schedule:
            if self.get_by_model_attr:
                visit_schedule, _ = site_visit_schedules.get_by_model(
                    attr=self.get_by_model_attr, model=self._meta.model._meta.label_lower
                )
            else:
                raise VisitScheduleNonCrfModelFormMixinError(
                    "Unable to determine `visit schedule`. "
                    f"See model and modelform for {self._meta.model}."
                )
        return visit_schedule

    @property
    def schedule(self) -> Schedule:
        try:
            _, schedule = site_visit_schedules.get_by_model(
                attr=self.get_by_model_attr, model=self._meta.model._meta.label_lower
            )
        except SiteVisitScheduleError:
            schedule = self.instance.schedule
        return schedule

    def is_onschedule_or_raise(self) -> None:
        subject_schedule = SubjectSchedule(self.visit_schedule, self.schedule)
        try:
            subject_schedule.onschedule_or_raise(
                subject_identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
                compare_as_datetimes=self.offschedule_compare_dates_as_datetimes,
            )
        except (NotOnScheduleError, NotOnScheduleForDateError) as e:
            raise forms.ValidationError(str(e))

    def report_datetime_within_schedule_datetimes(self) -> None:
        report_datetime_within_onschedule_offschedule_datetimes(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            exception_cls=forms.ValidationError,
        )

    @property
    def offschedule_compare_dates_as_datetimes(self):
        return self._meta.model.offschedule_compare_dates_as_datetimes
