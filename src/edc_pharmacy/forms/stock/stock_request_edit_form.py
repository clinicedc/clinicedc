"""Form for creating/editing a StockRequest from the workflow page.

Date fields are date-only; the server appends time on save.
Validation logic mirrors StockRequestForm but adapted for workflow use.
"""

from __future__ import annotations

from clinicedc_constants import CANCEL
from django import forms
from django.utils import timezone

from ...models import Allocation, Container, StockRequest
from ...models.stock.location import Location


class StockRequestEditForm(forms.ModelForm):
    request_date = forms.DateField(
        label="Request date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )
    start_date = forms.DateField(
        label="Start date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Exclude appointments before this date. Leave blank to include all.",
    )
    cutoff_date = forms.DateField(
        label="Cutoff date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Exclude appointments after this date.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.filter(
            site_id__isnull=False
        ).order_by("display_name")
        self.fields["container"].queryset = Container.objects.filter(
            may_request_as=True
        ).order_by("name")
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Textarea)):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()
        # Pre-fill date fields from instance datetimes
        if self.instance and self.instance.pk:
            if self.instance.request_datetime:
                self.initial["request_date"] = timezone.localtime(
                    self.instance.request_datetime
                ).date()
            if self.instance.start_datetime:
                self.initial["start_date"] = timezone.localtime(
                    self.instance.start_datetime
                ).date()
            if self.instance.cutoff_datetime:
                self.initial["cutoff_date"] = timezone.localtime(
                    self.instance.cutoff_datetime
                ).date()
        else:
            self.initial.setdefault("request_date", timezone.localtime(timezone.now()).date())

    def clean_request_date(self):
        date = self.cleaned_data.get("request_date")
        if date and date > timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Request date may not be a future date.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        request_date = cleaned_data.get("request_date")
        start_date = cleaned_data.get("start_date")
        cutoff_date = cleaned_data.get("cutoff_date")

        if request_date and cutoff_date and cutoff_date <= request_date:
            self.add_error("cutoff_date", "Must be after the request date.")
        if start_date and request_date and start_date > request_date:
            self.add_error("start_date", "Must be on or before the request date.")
        if start_date and cutoff_date and start_date >= cutoff_date:
            self.add_error("cutoff_date", "Must be at least 1 day after start date.")

        if cleaned_data.get("subject_identifiers") and cleaned_data.get(
            "excluded_subject_identifiers"
        ):
            raise forms.ValidationError(
                "Cannot include and exclude subject identifiers in the same request."
            )

        container = cleaned_data.get("container")
        containers_per_subject = cleaned_data.get("containers_per_subject")
        if (
            container
            and containers_per_subject
            and containers_per_subject > container.max_items_per_subject
        ):  # noqa: E501
            self.add_error(
                "containers_per_subject",
                f"May not exceed {container.max_items_per_subject} for this container.",
            )

        if (
            self.instance
            and self.instance.pk
            and cleaned_data.get("cancel") == CANCEL
            and Allocation.objects.filter(
                stock_request_item__stock_request=self.instance
            ).exists()
        ):
            raise forms.ValidationError(
                "May not be cancelled — stock has already been allocated."
            )

        return cleaned_data

    class Meta:
        model = StockRequest
        fields = (
            "request_date",
            "start_date",
            "cutoff_date",
            "location",
            "formulation",
            "container",
            "containers_per_subject",
            "visit_schedules",
            "subject_identifiers",
            "excluded_subject_identifiers",
        )
        widgets = {  # noqa: RUF012
            "subject_identifiers": forms.Textarea(attrs={"rows": 4}),
            "excluded_subject_identifiers": forms.Textarea(attrs={"rows": 4}),
        }
