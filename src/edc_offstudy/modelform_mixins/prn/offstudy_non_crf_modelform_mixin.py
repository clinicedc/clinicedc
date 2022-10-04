from django import forms

from ...exceptions import OffstudyError
from ...utils import raise_if_offstudy


class OffstudyNonCrfModelFormMixin:
    """ModelForm mixin for non-CRF modelforms / PRNs."""

    def clean(self):
        cleaned_data = super().clean()
        self.raise_if_offstudy_by_report_datetime()
        return cleaned_data

    def raise_if_offstudy_by_report_datetime(self) -> None:
        if self.subject_identifier and self.report_datetime:
            try:
                raise_if_offstudy(
                    source_obj=self.instance,
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.report_datetime,
                )
            except OffstudyError as e:
                raise forms.ValidationError(e)
