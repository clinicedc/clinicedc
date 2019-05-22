from django import forms
from edc_visit_schedule.subject_schedule import (
    NotOnScheduleError,
    NotOnScheduleForDateError,
)


class SubjectScheduleCrfModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        subject_visit = cleaned_data.get(self._meta.model.visit_model_attr())
        if subject_visit:
            visit_schedule = subject_visit.appointment.visit_schedule
            schedule = subject_visit.appointment.schedule
            subject_schedule = self._meta.model.subject_schedule_cls(
                visit_schedule=visit_schedule, schedule=schedule
            )
            try:
                subject_schedule.onschedule_or_raise(
                    subject_identifier=subject_visit.subject_identifier,
                    report_datetime=subject_visit.report_datetime,
                    compare_as_datetimes=(
                        self._meta.model.offschedule_compare_dates_as_datetimes
                    ),
                )
            except (NotOnScheduleError, NotOnScheduleForDateError) as e:
                raise forms.ValidationError(str(e))
        return cleaned_data
