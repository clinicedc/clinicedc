from django import forms

from ...models import Receive


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Receive
        fields = "__all__"
        help_text = {"receive_identifier": "(read-only)"}
        widgets = {
            "receive_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
