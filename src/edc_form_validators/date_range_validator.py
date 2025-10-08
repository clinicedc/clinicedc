from __future__ import annotations

import contextlib
from datetime import date

from django import forms
from django.utils.translation import gettext as _

from edc_utils.date import to_local

from .base_form_validator import BaseFormValidator


def convert_any_to_date(date1, date2) -> tuple[date, date]:
    with contextlib.suppress(AttributeError):
        date1 = to_local(date1).date()
    with contextlib.suppress(AttributeError):
        date2 = to_local(date2).date()
    return date1, date2


class DateRangeFieldValidator(BaseFormValidator):
    def date_not_before(
        self,
        date_field1: str,
        date_field2: str,
        msg=None,
        convert_to_date: bool | None = None,
        message_on_field=None,
    ) -> None:
        """Asserts date_field2 is not before date_field1"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        if convert_to_date:
            date1, date2 = convert_any_to_date(date1, date2)
        if date1 and date2 and (date2 < date1):
            msg = msg or _("Invalid. Cannot be before %(field)s.") % {"field": date_field1}
            raise forms.ValidationError({message_on_field or date_field2: msg})

    def date_not_after(
        self,
        date_field1: str,
        date_field2: str,
        msg: str | None = None,
        convert_to_date: bool | None = None,
    ) -> None:
        """Asserts date_field2 is not after date_field1"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        if convert_to_date:
            date1, date2 = convert_any_to_date(date1, date2)
        if date1 and date2 and (date2 > date1):
            msg = msg or _("Invalid. Cannot be after %(field)s.") % {"field": date_field1}
            raise forms.ValidationError({date_field2: msg})

    def date_equal(
        self,
        date_field1: str,
        date_field2: str,
        msg=None,
        message_on_field=None,
        convert_to_date: bool | None = None,
    ) -> None:
        """Asserts date2 and date1 are equal"""
        date1 = self.cleaned_data.get(date_field1)
        date2 = self.cleaned_data.get(date_field2)
        if convert_to_date:
            date1, date2 = convert_any_to_date(date1, date2)
        if date1 and date2 and (date1 != date2):
            msg = msg or _("Invalid. Expected %(field2)s to be the same as %(field1)s.") % {
                "field1": date_field1,
                "field2": date_field2,
            }
            raise forms.ValidationError({message_on_field or date_field2: msg})

    def date_not_equal(
        self,
        date_field1: str,
        date_field2: str,
        msg=None,
        message_on_field=None,
        convert_to_date: bool | None = None,
    ) -> None:
        """Asserts date2 and date1 are not equal"""
        dte1 = self.cleaned_data.get(date_field1)
        dte2 = self.cleaned_data.get(date_field2)
        if convert_to_date:
            dte1, dte2 = convert_any_to_date(dte1, dte2)
        if dte1 and dte2 and (dte1 == dte2):
            msg = msg or _("Invalid. Expected %(field2)s to be different from %(field1)s.") % {
                "field1": date_field1,
                "field2": date_field2,
            }
            raise forms.ValidationError({message_on_field or date_field2: msg})

    def datetime_not_before(
        self, datetime_field1: str, datetime_field2: str, msg=None
    ) -> None:
        """Asserts datetime_field2 is not before datetime_field1"""
        dte1 = self.cleaned_data.get(datetime_field1)
        dte2 = self.cleaned_data.get(datetime_field2)
        if dte1 and dte2 and (dte2 < dte1):
            msg = msg or _("Invalid. Cannot be before %(field)s") % {"field": datetime_field1}
            raise forms.ValidationError({datetime_field2: msg})

    def datetime_not_after(self, datetime_field1: str, datetime_field2: str, msg=None) -> None:
        """Asserts datetime_field2 is not after datetime_field1"""
        dte1 = self.cleaned_data.get(datetime_field1)
        dte2 = self.cleaned_data.get(datetime_field2)
        if dte1 and dte2 and (dte2 > dte1):
            msg = msg or _("Invalid. Cannot be after %(field)s") % {"field": datetime_field1}
            raise forms.ValidationError({datetime_field2: msg})

    def datetime_equal(self, datetime_field1: str, datetime_field2: str, msg=None) -> None:
        """Asserts datetime_field2 is not equal to datetime_field1"""
        dte1 = self.cleaned_data.get(datetime_field1)
        dte2 = self.cleaned_data.get(datetime_field2)
        if dte1 and dte2 and (dte1 == dte2):
            msg = msg or _("Invalid. Cannot be same as %(field)s") % {"field": datetime_field1}
            raise forms.ValidationError({datetime_field2: msg})
