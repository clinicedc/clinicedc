from django import forms

from ..models import DispensedItem


class DispensedItemForm(forms.ModelForm):

    class Meta:
        model = DispensedItem
        fields = '__all__'


class DispensedItemReadonlyForm(forms.ModelForm):

    count = forms.DecimalField(
        label='Count',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    status = forms.ChoiceField(
        label='Status',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    dispensed_datetime = forms.DateTimeField(
        label='Dispensed Datetime',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = DispensedItem
        # ['medication', 'count', 'status', 'dispensed_datetime']
        # fields = '__all__'
        exclude = ['medication']
