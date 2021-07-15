from django import forms
from edc_model.utils import InvalidFormat, duration_to_date


class EstimatedDateFromAgoFormMixin:
    def estimated_date_from_ago(self, f1):
        """Returns the estimated date using `duration_to_date` or None."""
        estimated_date = None
        if self.cleaned_data.get(f1):
            try:
                estimated_date = duration_to_date(
                    self.cleaned_data.get(f1),
                    self.cleaned_data.get("report_datetime").date(),
                )
            except InvalidFormat as e:
                raise forms.ValidationError({f1: str(e)})
        return estimated_date
