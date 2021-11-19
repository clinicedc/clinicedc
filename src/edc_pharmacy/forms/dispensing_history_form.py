from django import forms

from ..constants import DISPENSED
from ..dispensing import DispenseError, Dispensing
from ..models import DispensingHistory


class DispensingHistoryForm(forms.ModelForm):
    def clean(self):
        try:
            Dispensing(
                self.cleaned_data.get("rx_refill"),
                dispensed=self.cleaned_data.get("dispensed"),
                exclude_id=self.cleaned_data.get("id"),
            )
        except DispenseError as e:
            raise forms.ValidationError(e)

    class Meta:
        model = DispensingHistory
        fields = "__all__"


class DispensingHistoryReadonlyForm(forms.ModelForm):

    count = forms.DecimalField(
        label="Count", widget=forms.TextInput(attrs={"readonly": "readonly"})
    )

    status = forms.CharField(
        label="Status",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    dispensed_datetime = forms.DateTimeField(
        label="Dispensed Datetime",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = DispensingHistory
        # ['medication', 'count', 'status', 'dispensed_datetime']
        # fields = '__all__'
        exclude = ["medication"]
