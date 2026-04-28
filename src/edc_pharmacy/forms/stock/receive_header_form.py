"""Form for creating/editing a Receive header on the receive workflow page.

Deliberately excludes AUDIT_MODEL_FIELDS (created, modified, user_created,
user_modified, hostname_created, hostname_modified, device_created,
device_modified, locale_created, locale_modified) — these are SYSTEM_COLUMNS
managed by django_audit_fields and are never edited by users in any context.
Also excludes receive_identifier (auto-assigned).
"""

import datetime

from django import forms
from django.utils import timezone

from ...models import Receive, ReceiveItem


class ReceiveHeaderForm(forms.ModelForm):
    """Receive header form for the receive workflow page.

    receive_date is a date-only field; the server appends the current time
    when saving. The date may not be in the future.
    """

    receive_date = forms.DateField(
        label="Receive date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item_count"].required = True
        self.fields["invoice_number"].required = True
        self.fields["invoice_date"].required = True
        self.fields["invoice_date"].input_formats = ["%Y-%m-%d"]
        self.fields["invoice_date"].widget = forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        )
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()
        # Pre-fill receive_date from the existing receive_datetime (if editing)
        if self.instance and self.instance.pk and self.instance.receive_datetime:
            self.initial["receive_date"] = timezone.localtime(
                self.instance.receive_datetime
            ).date()
        else:
            self.initial.setdefault("receive_date", timezone.localtime(timezone.now()).date())

    def clean_receive_date(self):
        date = self.cleaned_data.get("receive_date")
        if date and date > timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Receive date may not be a future date.")
        return date

    def clean_invoice_date(self):
        date = self.cleaned_data.get("invoice_date")
        if date and date > timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Invoice date may not be a future date.")
        return date

    def clean_item_count(self):
        item_count = self.cleaned_data.get("item_count")
        if item_count is None:
            # field is required; Django's required check fires first, but guard here too
            raise forms.ValidationError("This field is required.")
        if item_count < 1:
            raise forms.ValidationError("Item count must be a positive integer greater than 0.")
        if self.instance and self.instance.pk:
            received = ReceiveItem.objects.filter(receive=self.instance).count()
            if item_count < received:
                raise forms.ValidationError(
                    f"Item count may not be less than the number of receive items "
                    f"already recorded ({received})."
                )
        return item_count

    def clean(self):
        return super().clean()

    class Meta:
        model = Receive
        fields = [
            "receive_date",
            "location",
            "item_count",
            "invoice_number",
            "invoice_date",
            "comment",
        ]
        widgets = {
            "invoice_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }
