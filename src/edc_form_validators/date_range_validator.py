from django import forms
from edc_utils.date import to_utc
from edc_utils.text import formatted_datetime

from .base_form_validator import BaseFormValidator


class DateRangeFieldValidator(BaseFormValidator):
    def date_not_before(
        self,
        date_field1: str,
        date_field2: str,
        msg=None,
        convert_to_date=None,
        message_on_field=None,
    ) -> None:
        """Asserts date_field2 is not before date_field1"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        if convert_to_date:
            try:
                date1 = date1.date()
            except AttributeError:
                pass
            try:
                date2 = date2.date()
            except AttributeError:
                pass

        msg = msg or f"Invalid. Cannot be before {date_field1} "
        if date1 and date2:
            if date1 > date2:
                raise forms.ValidationError({message_on_field or date_field2: f"{msg}."})

    def date_not_after(self, date_field1: str, date_field2: str, msg=None) -> None:
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        msg = msg or f"Invalid. Cannot be after {date_field1} "
        if date1 and date2:
            if date1 < date2:
                raise forms.ValidationError({date_field2: f"{msg}"})

    def date_equal(
        self, date_field1: str, date_field2: str, msg=None, message_on_field=None
    ) -> None:
        """Asserts date1 and date2 are equal"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        msg = msg or f"Invalid. Expected {date_field2} to be the same as {date_field1}."
        if date1 and date2:
            print(date1, date2)
            if date1 != date2:
                raise forms.ValidationError({message_on_field or date_field2: f"{msg}"})

    def date_not_equal(
        self, date_field1: str, date_field2: str, msg=None, message_on_field=None
    ) -> None:
        """Asserts date1 and date2 are equal"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        msg = msg or f"Invalid. Expected {date_field2} to be the same as {date_field1}."
        if date1 and date2:
            print(date1, date2)
            if date1 == date2:
                raise forms.ValidationError({message_on_field or date_field2: f"{msg}"})

    def datetime_not_before(
        self, datetime_field1: str, datetime_field2: str, msg=None
    ) -> None:
        datetime1 = self.cleaned_data.get(datetime_field1)
        datetime2 = self.cleaned_data.get(datetime_field2)
        if datetime1:
            datetime1 = to_utc(datetime1)
        if datetime2:
            datetime2 = to_utc(datetime2)
        msg = msg or f"Invalid. Cannot be before {datetime_field2} "
        if datetime1 and datetime2:
            if datetime1 < datetime2:
                raise forms.ValidationError(
                    {datetime_field1: f"{msg}. Got {formatted_datetime(datetime2)}."}
                )

    def datetime_not_after(self, datetime_field1: str, datetime_field2: str, msg=None) -> None:
        datetime_field1 = self.cleaned_data.get(datetime_field1)
        datetime_field2 = self.cleaned_data.get(datetime_field2)
        msg = msg or f"Invalid. Cannot be before date of {datetime_field2} "
        if datetime_field1:
            datetime_field1 = to_utc(datetime_field1)
            datetime_field2 = to_utc(datetime_field2)
            if datetime_field1 > datetime_field2:
                raise forms.ValidationError({datetime_field1: f"{msg}"})

    def datetime_equal(self, datetime_field1: str, datetime_field2: str, msg=None) -> None:
        datetime_field1 = self.cleaned_data.get(datetime_field1)
        datetime_field2 = self.cleaned_data.get(datetime_field2)
        msg = msg or f"Invalid. Cannot be before date of {datetime_field2} "
        if datetime_field1:
            datetime_field1 = to_utc(datetime_field1)
            datetime_field2 = to_utc(datetime_field2)
            if datetime_field1 == datetime_field2:
                raise forms.ValidationError(
                    {datetime_field1: f"{msg}. Got {formatted_datetime(datetime_field2)}."}
                )
