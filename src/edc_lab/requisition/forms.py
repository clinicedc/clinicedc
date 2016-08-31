from django import forms

from edc_constants.constants import YES, NO


class RequisitionFormMixin(forms.ModelForm):

    def clean(self):
        cleaned_data = super(RequisitionFormMixin, self).clean()
        if cleaned_data.get('is_drawn').lower() == YES and not cleaned_data.get('drawn_datetime'):
            raise forms.ValidationError("A specimen was collected. Please provide the date and time collected.")
        if cleaned_data.get('is_drawn').lower() == NO and not cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError("Please provide a reason why the specimen was not collected.")
        if cleaned_data.get('is_drawn').lower() == YES and cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError(
                "A specimen was not drawn. Do not provided a reason why it was not collected.")
        return cleaned_data
