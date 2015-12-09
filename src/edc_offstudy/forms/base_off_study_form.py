from django import forms

from edc.subject.consent.forms import BaseConsentedModelForm


class BaseOffStudyForm(BaseConsentedModelForm):

    """Used to edit the off study form and throws an exception if the off study date is invalid."""

    def clean(self):
        cleaned_data = self.cleaned_data
        self._meta.model().check_off_study_date(cleaned_data.get('registered_subject').get_subject_identifier(), cleaned_data.get('offstudy_date'), exception_cls=forms.ValidationError)
        return super(BaseOffStudyForm, self).clean()
