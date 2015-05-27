from django import forms


class BaseRequisitionForm (forms.ModelForm):

    def clean(self):

        cleaned_data = self.cleaned_data
        if cleaned_data.get('is_drawn').lower() == 'yes' and not cleaned_data.get('drawn_datetime'):
            raise forms.ValidationError("Date and Time Drawn must be provided if a sample was drawn.")
        if cleaned_data.get('is_drawn').lower() == 'no' and not cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError("Please provide a reason why sample was not drawn.")
        if cleaned_data.get('is_drawn').lower() == 'yes' and cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError(
                'You have provided a reason why sample was not drawn yet '
                'indicate that it was drawn. Please correct.')
        return cleaned_data
