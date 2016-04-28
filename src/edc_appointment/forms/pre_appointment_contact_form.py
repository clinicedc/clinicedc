from django import forms
from django.contrib.admin.widgets import AdminRadioSelect, AdminRadioFieldRenderer

from edc_constants.constants import YES, NO

from ..choices import INFO_PROVIDER
from ..models import PreAppointmentContact


class PreAppointmentContactForm (forms.ModelForm):

    information_provider = forms.ChoiceField(
        label='Who answered?',
        choices=[('', 'None')] + list(INFO_PROVIDER),
        required=False,
        widget=AdminRadioSelect(renderer=AdminRadioFieldRenderer))

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('is_contacted', None):
            raise forms.ValidationError('Please select Yes or No')
        if cleaned_data.get('is_contacted') == NO and cleaned_data.get('information_provider'):
            raise forms.ValidationError(
                'You wrote contact was NOT made yet have recorded the information provider. Please correct.')
        if cleaned_data.get('is_contacted') == YES and not cleaned_data.get('information_provider'):
            raise forms.ValidationError(
                'You wrote contact was made. Please indicate the information provider. Please correct.')
        return super(PreAppointmentContactForm, self).clean()

    class Meta:
        model = PreAppointmentContact
        fields = '__all__'
