from django import forms


class BaseConsentUpdateForm (forms.ModelForm):
    def clean(self, consent_instance_field_name, consent_instance=None):
        cleaned_data = self.cleaned_data
        consent_version = cleaned_data.get('consent_version', None)
        if not consent_version and consent_instance:
            options = {consent_instance_field_name: consent_instance, 'consent_version': consent_version}
            if self._meta.model.objects.filter(**options).exists() and not cleaned_data.get('id', None):
                raise forms.ValidationError(
                    'Consent update for edc_consent version {0} already exists.'.format(consent_version))
        return cleaned_data
