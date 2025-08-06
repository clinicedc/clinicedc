from django import forms

from ...models import Receive, ReceiveItem


class ReceiveForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if (
            getattr(self.instance, "id", None)
            and ReceiveItem.objects.filter(receive=self.instance).exists()
        ):
            raise forms.ValidationError("Receive record cannot be changed.")
        return cleaned_data

    class Meta:
        model = Receive
        fields = "__all__"
        help_text = {"receive_identifier": "(read-only)"}
        widgets = {
            "receive_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }


class ReceiveFormSuper(forms.ModelForm):
    class Meta:
        model = Receive
        fields = "__all__"
        help_text = {"receive_identifier": "(read-only)"}
        widgets = {
            "receive_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
