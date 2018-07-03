from django import forms

from ..offstudy import Offstudy, OffstudyError


class OffstudyModelFormMixin(forms.ModelForm):

    """ModelForm mixin for the Offstudy Model.
    """

    offstudy_cls = Offstudy

    def clean(self):
        cleaned_data = super().clean()
        offstudy_model = self._meta.model._meta.label_lower
        try:
            cleaned_data['subject_identifier'] = (
                cleaned_data.get('subject_identifier') or self.instance.subject_identifier)
            self.offstudy_cls(
                offstudy_model=offstudy_model,
                **cleaned_data)
        except OffstudyError as e:
            raise forms.ValidationError(e)
        return cleaned_data
