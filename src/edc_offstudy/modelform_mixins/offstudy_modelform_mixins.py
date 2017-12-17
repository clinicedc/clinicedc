from django import forms

from ..offstudy import Offstudy, OffstudyError


class OffstudyModelFormMixin(forms.ModelForm):

    """ModelForm mixin for the Offstudy Model.
    """

    offstudy_cls = Offstudy

    def clean(self):
        cleaned_data = super().clean()
        consent_model = self._meta.model._meta.consent_model
        label_lower = self._meta.model._meta.label_lower
        try:
            self.offstudy_cls(
                consent_model=consent_model,
                label_lower=label_lower, **cleaned_data)
        except OffstudyError as e:
            raise forms.ValidationError(e)
        return cleaned_data
