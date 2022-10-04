from django import forms

from ... import Schedule, VisitSchedule
from ...subject_schedule import (
    NotOnScheduleError,
    NotOnScheduleForDateError,
    SubjectSchedule,
)
from ...utils import report_datetime_within_onschedule_offschedule_datetimes


class VisitScheduleCrfModelFormMixin:
    """A ModelForm mixin for CRFs to validate that the subject is
    onschedule at the time of the report.

    Required to be declared together with other Crf modelform mixins.

    See also CrfModelFormMixin
    """

    def clean(self):
        cleaned_data = super().clean()
        self.is_onschedule_or_raise()
        self.report_datetime_within_schedule_datetimes()
        return cleaned_data

    @property
    def visit_schedule_name(self) -> str:
        return self.related_visit.visit_schedule_name

    @property
    def schedule_name(self) -> str:
        return self.related_visit.schedule_name

    @property
    def visit_schedule(self) -> VisitSchedule:
        return self.related_visit.visit_schedule

    @property
    def schedule(self) -> Schedule:
        return self.related_visit.schedule

    def is_onschedule_or_raise(self) -> None:
        if self.report_datetime and self.related_visit:
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            subject_schedule = SubjectSchedule(visit_schedule, schedule)
            try:
                subject_schedule.onschedule_or_raise(
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.report_datetime,
                    compare_as_datetimes=(
                        self._meta.model.offschedule_compare_dates_as_datetimes
                    ),
                )
            except (NotOnScheduleError, NotOnScheduleForDateError) as e:
                raise forms.ValidationError(str(e))

    def report_datetime_within_schedule_datetimes(self) -> None:
        if self.report_datetime:
            report_datetime_within_onschedule_offschedule_datetimes(
                subject_identifier=self.subject_identifier,
                report_datetime=self.report_datetime,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                exception_cls=forms.ValidationError,
            )
