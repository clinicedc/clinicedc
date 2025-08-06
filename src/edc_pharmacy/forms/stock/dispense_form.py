from django import forms

from ...models import Dispense


class DispenseForm(forms.ModelForm):
    class Meta:
        model = Dispense
        fields = "__all__"
        help_text = {"dispense_identifier": "(read-only)"}
        widgets = {
            "dispense_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
