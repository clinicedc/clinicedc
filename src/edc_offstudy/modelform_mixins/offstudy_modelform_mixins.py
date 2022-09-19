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
        self.cleaned_data["subject_identifier"] = (
            self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier
        )
        self.off_all_schedules_or_raise()
        self.offstudy_datetime_after_all_offschedule_datetimes()
        return cleaned_data

    def off_all_schedules_or_raise(self):
        try:
            off_all_schedules_or_raise(
                subject_identifier=self.cleaned_data.get("subject_identifier")
            )
        except OffScheduleError as e:
            raise forms.ValidationError(e)

    def offstudy_datetime_after_all_offschedule_datetimes(self):
        offstudy_datetime_after_all_offschedule_datetimes(
            subject_identifier=self.cleaned_data.get("subject_identifier"),
            offstudy_datetime=self.cleaned_data.get("offstudy_datetime"),
        )
