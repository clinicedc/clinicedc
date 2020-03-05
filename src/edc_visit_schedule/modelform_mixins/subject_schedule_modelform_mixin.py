from django import forms

from ..subject_schedule import (
    NotOnScheduleError,
    NotOnScheduleForDateError,
)


class SubjectScheduleModelFormMixin:
    """A ModelForm mixin to validate that the subject is onschedule.

    Declare with `forms.ModelForm`.

    See `self._meta.model.visit_model_attr()`.
    """

    def clean(self):
        cleaned_data = super().clean()
        subject_visit = cleaned_data.get(self._meta.model.visit_model_attr())
        if subject_visit:
            visit_schedule = subject_visit.appointment.visit_schedule
            schedule = subject_visit.appointment.schedule
            subject_schedule = self.get_subject_schedule(visit_schedule, schedule)
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

    def get_subject_schedule(self, visit_schedule, schedule):
        try:
            subject_schedule = self._meta.model.subject_schedule_cls(
                visit_schedule=visit_schedule, schedule=schedule
            )
        except AttributeError as e:
            if "subject_schedule_cls" in str(e):
                raise AttributeError(
                    f"Was model `{self._meta.model._meta.label_lower}` declared "
                    f"with `SubjectScheduleModelMixin`? Got {e}"
                )
            else:
                raise
        return subject_schedule
