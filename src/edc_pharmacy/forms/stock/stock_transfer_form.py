from django import forms

from ...constants import CENTRAL_LOCATION
from ...models import StockTransfer


class StockTransferForm(forms.ModelForm):
    @property
    def to_location(self):
        return self.cleaned_data.get("to_location") or self.instance.to_location

    @property
    def from_location(self):
        return self.cleaned_data.get("from_location") or self.instance.from_location

    def clean(self):
        cleaned_data = super().clean()

        # assuming all fields expect 'comment' are set to readonly on EDIT
        if not self.instance.id:
            # TO/FROM locations cannot be the same
            if self.to_location == self.from_location:
                raise forms.ValidationError(
                    {
                        "__all__": "Invalid location combination. 'TO' and 'FROM' locations "
                        "cannot be the same"
                    }
                )

            # at least one location must be CENTRAL
            if CENTRAL_LOCATION not in [self.to_location.name, self.from_location.name]:
                raise forms.ValidationError(
                    {"__all__": "Invalid location combination. One location must be Central"}
                )

        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = "__all__"
        help_text = {"transfer_identifier": "(read-only)"}  # noqa: RUF012
        widgets = {  # noqa: RUF012
            "transfer_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
