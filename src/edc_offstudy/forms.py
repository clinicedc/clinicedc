from django import forms


class BaseOffStudyForm(forms.ModelForm):

    """Used to edit the off study form and throws an exception
    if the off study date is invalid."""

    def clean(self):
        cleaned_data = super(BaseOffStudyForm, self).clean()
        self._meta.model(**cleaned_data).off_study_date_or_raise(
            cleaned_data.get('registered_subject').get_subject_identifier(),
            cleaned_data.get('offstudy_date'),
            exception_cls=forms.ValidationError)
        return cleaned_data
