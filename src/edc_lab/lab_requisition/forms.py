from django import forms

from edc_constants.constants import YES, NO


class RequisitionFormMixin(forms.ModelForm):

    def clean(self):
        cleaned_data = super(RequisitionFormMixin, self).clean()
        if cleaned_data.get('is_drawn').lower() == YES and not cleaned_data.get('drawn_datetime'):
            raise forms.ValidationError("Date and Time Drawn must be provided if a sample was drawn.")
        if cleaned_data.get('is_drawn').lower() == NO and not cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError("Please provide a reason why sample was not drawn.")
        if cleaned_data.get('is_drawn').lower() == YES and cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError(
                "You have provided a reason why sample was not drawn yet indicate that it was drawn. Please correct.")
        return cleaned_data
