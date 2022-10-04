from django import forms
from edc_visit_schedule.exceptions import OffScheduleError
from edc_visit_schedule.utils import (
    off_all_schedules_or_raise,
    offstudy_datetime_after_all_offschedule_datetimes,
)


class OffstudyModelFormMixin:

    """ModelForm mixin for the Offstudy Model."""

    def clean(self):
        cleaned_data = super().clean()
        self.off_all_schedules_or_raise()
        self.offstudy_datetime_after_all_offschedule_datetimes()
        return cleaned_data

    def off_all_schedules_or_raise(self):
        """Raises a ValidationError if this off study form is submitted
        but subject is still on one or more schedules.
        """
        try:
            off_all_schedules_or_raise(subject_identifier=self.subject_identifier)
        except OffScheduleError as e:
            raise forms.ValidationError(e)

    def offstudy_datetime_after_all_offschedule_datetimes(self):
        """Raises a ValidationError if any offschedule datetime is after
        this offstudy_datetime.
        """
        offstudy_datetime_after_all_offschedule_datetimes(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.cleaned_data.get("offstudy_datetime"),
            exception_cls=forms.ValidationError,
        )
