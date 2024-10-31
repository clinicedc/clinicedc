from django import forms

from ...models import Receive


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Receive
        fields = "__all__"
