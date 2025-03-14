from django import forms

from ...models import StorageBin


class StorageBinForm(forms.ModelForm):

    class Meta:
        model = StorageBin
        fields = "__all__"
