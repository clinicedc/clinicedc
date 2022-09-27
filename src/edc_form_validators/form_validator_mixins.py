from __future__ import annotations

from datetime import datetime

from django.forms import ModelForm
from edc_utils import to_utc


class FormValidatorMixin:
    """A ModelForm mixin to add a validator class.

    Declare with `forms.ModelForm`.
    """

    form_validator_cls = None

    def clean(self: ModelForm) -> dict:
        cleaned_data = super().clean()
        try:
            form_validator = self.form_validator_cls(
                cleaned_data=cleaned_data,
                instance=self.instance,
                data=self.data,
                model=self._meta.model,
            )
        except TypeError as e:
            if str(e) != "'NoneType' object is not callable":
                raise
        else:
            cleaned_data = form_validator.validate()
        return cleaned_data


class ReportDatetimeFormValidatorMixin:

    report_datetime_field_attr: str = None

    @property
    def report_datetime(self) -> datetime | None:
        """Returns the report_datetime in UTC from cleaned_data,
        if key exists, else returns the instance report_datetime.
        """
        if self.report_datetime_field_attr in self.cleaned_data:
            return to_utc(self.cleaned_data.get(self.report_datetime_field_attr))
        else:
            return getattr(self.instance, self.report_datetime_field_attr)
