from django import forms
from django.apps import apps as django_apps


class OffstudyModelFormMixin(forms.ModelForm):

    """Form Mixin for the Offstudy Model.

    Used to edit the off study form and throws an exception
    if the off study date is invalid.
    """

    def clean(self):
        cleaned_data = super().clean()
        self.validate_offstudy_datetime()
        return cleaned_data

    def validate_offstudy_datetime(self):
        cleaned_data = self.cleaned_data
        consent_model = django_apps.get_model(
            self._meta.model._meta.consent_model)
        try:
            subject_identifier = cleaned_data.get('subject_identifier')
            consent_obj = consent_model.objects.get(
                subject_identifier=subject_identifier)
            try:
                offstudy_datetime = cleaned_data.get('offstudy_datetime')
                if offstudy_datetime < consent_obj.consent_datetime:
                    raise forms.ValidationError(
                        f"Off study date cannot be before consent date."
                        f"Got Offstudy date: {offstudy_datetime} less than dob: "
                        f"{consent_obj.consent_datetime}")
                if offstudy_datetime.date() < consent_obj.dob:
                    raise forms.ValidationError(
                        "Off study date cannot be before dob. "
                        f"Got Offstudy date: {offstudy_datetime} less than dob: "
                        f"{consent_obj.dob}")
            except AttributeError:
                pass
        except consent_model.DoesNotExist:
            raise forms.ValidationError('Consent does not exist.')

    class Meta:
        abstract = True
