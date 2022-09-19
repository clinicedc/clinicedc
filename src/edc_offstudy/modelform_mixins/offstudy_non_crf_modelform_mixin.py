from django import forms

from ..exceptions import OffstudyError
from ..utils import raise_if_offstudy


class OffstudyNonCrfModelFormMixin:
    """ModelForm mixin for non-CRF modelforms / PRNs."""

    report_datetime_field_attr = "report_datetime"

    def clean(self):
        cleaned_data = super().clean()
        self.cleaned_data["subject_identifier"] = (
            self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier
        )
        self.raise_if_offstudy()
        return cleaned_data

    def raise_if_offstudy(self) -> None:
        try:
            raise_if_offstudy(
                source_obj=self.instance,
                subject_identifier=self.cleaned_data.get("subject_identifier"),
                report_datetime=self.cleaned_data.get(self.report_datetime_field_attr),
                visit_schedule_name=getattr(self.instance, "visit_schedule_name", None),
                offstudy_model=getattr(self.instance, "offstudy_model", None),
            )
        except OffstudyError as e:
            raise forms.ValidationError(e)
