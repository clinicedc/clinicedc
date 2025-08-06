from django import forms

from ...models import ContainerUnits


class ContainerUnitsForm(forms.ModelForm):

    class Meta:
        model = ContainerUnits
        fields = "__all__"
