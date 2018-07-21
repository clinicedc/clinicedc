from django import forms

from ..offstudy_crf import SubjectOffstudyError
from ..offstudy_non_crf import OffstudyNonCrf


class OffstudyNonCrfModelFormMixin(forms.ModelForm):

    """ModelForm mixin for non-CRF modelforms.
    """

    offstudy_cls = OffstudyNonCrf

    def clean(self):
        cleaned_data = super().clean()
        offstudy_model = self._meta.model()._meta.offstudy_model
        try:
            self.offstudy_cls(offstudy_model=offstudy_model, **cleaned_data)
        except SubjectOffstudyError as e:
            raise forms.ValidationError({'report_datetime': e})
        return cleaned_data
