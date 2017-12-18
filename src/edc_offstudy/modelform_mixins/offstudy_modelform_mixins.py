from django import forms

from ..offstudy import Offstudy, OffstudyError
from pprint import pprint


class OffstudyModelFormMixin(forms.ModelForm):

    """ModelForm mixin for the Offstudy Model.
    """

    offstudy_cls = Offstudy

    def clean(self):
        cleaned_data = super().clean()
        consent_model = self._meta.model._meta.consent_model
        label_lower = self._meta.model._meta.label_lower
        try:
            cleaned_data['subject_identifier'] = (
                cleaned_data.get('subject_identifier') or self.instance.subject_identifier)
            self.offstudy_cls(
                consent_model=consent_model,
                label_lower=label_lower,
                visit_model_app_label=self._meta.model.offstudy_visit_model_app_label,
                **cleaned_data)
        except OffstudyError as e:
            raise forms.ValidationError(e)
        return cleaned_data
