from django import forms

from ...models import Lot


class LotForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("product") and cleaned_data.get("assignment"):
            if cleaned_data.get("product").assignment != cleaned_data.get("assignment"):
                raise forms.ValidationError(
                    {"assignment": "Assignment does not match product"}
                )

        return cleaned_data

    class Meta:
        model = Lot
        fields = "__all__"
