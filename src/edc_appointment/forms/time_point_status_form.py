from django import forms

from edc_constants.constants import NOT_APPLICABLE

from ..models import TimePointStatus


class TimePointStatusForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(TimePointStatusForm, self).clean()
        if cleaned_data.get('status') == 'feedback' and not cleaned_data.get('comment'):
            raise forms.ValidationError(
                'If feedback is being given, please provide a fully detailed description in the comment box below')

        if cleaned_data.get('subject_withdrew') == 'Yes' and cleaned_data.get('reasons_withdrawn') == NOT_APPLICABLE:
            raise forms.ValidationError('If subject is withdrawing, REASON for withdrawal cannot be NOT APPLICABLE')

        if cleaned_data.get('subject_withdrew') == 'Yes' and not cleaned_data.get('withdraw_datetime'):
            raise forms.ValidationError('If subject is withdrawing, please provide withdrawal date')

        self.instance.validate_status(TimePointStatus(**cleaned_data), forms.ValidationError)
        return cleaned_data

    class Meta:
        model = TimePointStatus
