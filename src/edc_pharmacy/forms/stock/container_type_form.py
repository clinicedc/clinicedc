from django import forms

from ...models import ContainerType


class ContainerTypeForm(forms.ModelForm):

    class Meta:
        model = ContainerType
        fields = "__all__"
