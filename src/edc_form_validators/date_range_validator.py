from django import forms
from edc_utils.date import to_utc
from edc_utils.text import formatted_date, formatted_datetime

from .base_form_validator import BaseFormValidator


class DateRangeFieldValidator(BaseFormValidator):
    def date_not_before(
        self, date_field: str, reference_date_field: str, msg=None, convert_to_date=None
    ) -> None:
        """Asserts date_field is not before reference_date_field.

        (raise if date_field > reference_date_field)
        """
        dte = self.cleaned_data.get(date_field)
        reference_dte = self.cleaned_data.get(reference_date_field)
        if convert_to_date:
            try:
                dte = dte.date()
            except AttributeError:
                pass
            try:
                reference_dte = reference_dte.date()
            except AttributeError:
                pass

        msg = msg or f"Invalid. Cannot be before {date_field} "
        if dte and reference_dte:
            if dte > reference_dte:
                raise forms.ValidationError(
                    {
                        reference_dte: (
                            f"{msg}. Got {formatted_date(reference_dte)} is "
                            f"before {formatted_date(dte)}."
                        )
                    }
                )

    def date_not_after(self, date_field1: str, reference_date_field: str, msg=None) -> None:
        """Asserts date_field1 is not after reference_date_field.

        (raise if date1 < date2)
        """
        dte = self.cleaned_data.get(date_field1)
        reference_dte = self.cleaned_data.get(reference_date_field)
        msg = msg or f"Invalid. Cannot be after {date_field1} "
        if dte and reference_dte:
            if dte < reference_dte:
                raise forms.ValidationError({reference_date_field: f"{msg}"})

    def date_equal(self, date_field1: str, date_field2: str, msg=None) -> None:
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        msg = msg or f"Invalid. Expected {date_field2} to be the same as {date_field1}."
        if date1 and date2:
            print(date1, date2)
            if date1 != date2:
                raise forms.ValidationError({date_field2: f"{msg}"})

    def datetime_not_before(
        self, datetime_field1: str, reference_datetime_field: str, msg=None
    ) -> None:
        dte = self.cleaned_data.get(datetime_field1)
        reference_datetime = self.cleaned_data.get(reference_datetime_field)
        if dte:
            dte = to_utc(dte)
        if reference_datetime:
            reference_datetime = to_utc(reference_datetime)
        msg = msg or f"Invalid. Cannot be before {reference_datetime_field} "
        if dte and reference_datetime:
            if dte < reference_datetime:
                raise forms.ValidationError(
                    {datetime_field1: f"{msg}. Got {formatted_datetime(reference_datetime)}."}
                )

    def datetime_not_after(
        self, datetime_field: str, reference_datetime_field: str, msg=None
    ) -> None:
        dte = self.cleaned_data.get(datetime_field)
        reference_datetime = self.cleaned_data.get(reference_datetime_field)
        msg = msg or f"Invalid. Cannot be before date of {reference_datetime} "
        if dte:
            dte = to_utc(dte)
            reference_datetime = to_utc(reference_datetime)
            if dte > reference_datetime:
                raise forms.ValidationError({datetime_field: f"{msg}"})

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
