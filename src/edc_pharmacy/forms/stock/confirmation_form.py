from django import forms

from ...models import Confirmation


class ConfirmationForm(forms.ModelForm):
    class Meta:
        model = Confirmation
        fields = "__all__"
        help_text = {"confirmation_identifier": "(read-only)"}  # noqa: RUF012
        widgets = {  # noqa: RUF012
            "confirmation_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
