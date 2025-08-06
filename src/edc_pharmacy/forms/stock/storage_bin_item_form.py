from django import forms

from ...models import StorageBinItem


class StorageBinItemForm(forms.ModelForm):

    class Meta:
        model = StorageBinItem
        fields = "__all__"
