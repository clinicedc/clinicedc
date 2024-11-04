from django import forms

from ...models import Request


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = "__all__"
        help_text = {"request_identifier": "(read-only)"}
        widgets = {
            "request_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
