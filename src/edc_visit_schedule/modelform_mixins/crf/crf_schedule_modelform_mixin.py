from django import forms

from ...subject_schedule import NotOnScheduleError, NotOnScheduleForDateError
from ...utils import (
    get_subject_schedule_cls,
    report_datetime_within_onschedule_offschedule_datetimes,
)


class CrfScheduleModelFormMixin:
    """A ModelForm mixin for CRFs to validate that the subject is onschedule.

    Declare with `forms.ModelForm`.

    See `self._meta.model.related_visit_model_attr()`.
    """

    report_datetime_field_attr = "report_datetime"

    def clean(self):
        cleaned_data = super().clean()
        self.is_onschedule_or_raise()
        self.report_datetime_within_schedule_datetimes()
        return cleaned_data

    def is_onschedule_or_raise(self) -> None:
        related_visit = (
            self.cleaned_data.get(self._meta.model.related_visit_model_attr())
            or self.instance.related_visit
        )
        if related_visit:
            visit_schedule = related_visit.appointment.visit_schedule
            schedule = related_visit.appointment.schedule
            subject_schedule = get_subject_schedule_cls(
                self._meta.model, visit_schedule, schedule
            )
            try:
                subject_schedule.onschedule_or_raise(
                    subject_identifier=related_visit.subject_identifier,
                    report_datetime=related_visit.report_datetime,
                    compare_as_datetimes=(
                        self._meta.model.offschedule_compare_dates_as_datetimes
                    ),
                )
            except (NotOnScheduleError, NotOnScheduleForDateError) as e:
                raise forms.ValidationError(str(e))

    def report_datetime_within_schedule_datetimes(self) -> None:
        report_datetime_within_onschedule_offschedule_datetimes(
            subject_identifier=self.related_visit.subject_identifier,
            report_datetime=self.cleaned_data.get(self.report_datetime_field_attr),
            visit_schedule_name=self.related_visit.visit_schedule_name,
            schedule_name=self.related_visit.schedule_name,
            exception_cls=forms.ValidationError,
        )
