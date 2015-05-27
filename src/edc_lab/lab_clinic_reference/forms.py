from django import forms


class GradingListItemForm(forms.ModelForm):

    def clean(self):

        cleaned_data = self.cleaned_data

        if cleaned_data.get('value_low', None) != 0 and  cleaned_data.get('value_low_calc', None) in ['LLN', 'ULN']:
            raise forms.ValidationError('If lower value is the {0}, set the value to 0.0. Got {1}'.format(cleaned_data.get('value_low_calc'), cleaned_data.get('value_low', None)))
        if cleaned_data.get('value_high', None) != 0 and  cleaned_data.get('value_high_calc', None) in ['LLN', 'ULN']:
            raise forms.ValidationError('If high value is the {0}, set the value to 0.0. Got {1}'.format(cleaned_data.get('value_high_calc'), cleaned_data.get('value_high', None)))
        return cleaned_data
