"""Form for editing an Order from the receive workflow page.

Excludes AUDIT_MODEL_FIELDS (SYSTEM_COLUMNS) and order_identifier (auto-assigned).
Status is managed by signal and shown read-only, not editable here.
order_date is date-only; the server appends the current time on save.
"""

from django import forms
from django.utils import timezone

from ...models import Order, OrderItem


class OrderEditForm(forms.ModelForm):
    order_date = forms.DateField(
        label="Order date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item_count"].required = True
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()
        # Cap the title at the model's max_length
        self.fields["title"].widget.attrs["maxlength"] = "50"
        if self.instance and self.instance.pk and self.instance.order_datetime:
            self.initial["order_date"] = timezone.localtime(
                self.instance.order_datetime
            ).date()
        else:
            self.initial.setdefault(
                "order_date", timezone.localtime(timezone.now()).date()
            )

    def clean_order_date(self):
        date = self.cleaned_data.get("order_date")
        if date and date > timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Order date may not be a future date.")
        return date

    def clean_item_count(self):
        item_count = self.cleaned_data.get("item_count")
        if item_count is not None:
            if item_count < 1:
                raise forms.ValidationError(
                    "Item count must be a positive integer greater than 0."
                )
            if self.instance and self.instance.pk:
                current = OrderItem.objects.filter(order=self.instance).count()
                if item_count < current:
                    raise forms.ValidationError(
                        f"Item count may not be less than the number of order items "
                        f"already added ({current})."
                    )
        return item_count

    class Meta:
        model = Order
        fields = [
            "order_date",
            "supplier",
            "title",
            "item_count",
            "sent",
            "comment",
        ]
