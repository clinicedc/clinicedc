from typing import Any, Optional

from django import forms
from edc_model.utils import InvalidFormat, duration_to_date


class EstimatedDateFromAgoFormMixin:
    def estimated_date_from_ago(
        self: Any, ago_field: str, reference_date_field: Optional[str] = None
    ):
        """Returns the estimated date using `duration_to_date` or None."""
        estimated_date = None
        reference_date_field = reference_date_field or "report_datetime"
        try:
            reference_date = self.cleaned_data.get(reference_date_field).date()
        except AttributeError:
            reference_date = self.cleaned_data.get(reference_date_field)

        if self.cleaned_data.get(ago_field):
            try:
                estimated_date = duration_to_date(
                    self.cleaned_data.get(ago_field),
                    reference_date,
                )
            except InvalidFormat as e:
                raise forms.ValidationError({ago_field: str(e)})
        return estimated_date

    def raise_if_both_ago_and_actual_date(
        self: Any,
        ago_field: Optional[str] = None,
        date_field: Optional[str] = None,
        label: Optional[str] = None,
    ):
        ago_field = ago_field or "dx_ago"
        date_field = date_field or "dx_date"
        label = label or "diagnosis"
        if self.cleaned_data.get(ago_field) and self.cleaned_data.get(date_field):
            raise forms.ValidationError(
                {
                    ago_field: (
                        "Date conflict. Do not provide a response "
                        f"here if the exact {label} date is available."
                    )
                }
            )
