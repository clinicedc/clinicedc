from django import forms

from edc_base.utils import convert_from_camel


class BaseConsentedModelForm(forms.ModelForm):

    """Base Form for all models that confirm a valid subject
    edc_consent to be available before allowing data collection.

    That is the "model" must be backed by a edc_consent.
    """

    def clean(self):
        """Checks if subject has a valid edc_consent for this subject
        model instance and versioned fields.
        """
        cleaned_data = self.cleaned_data
        try:
            appointment = cleaned_data.get(
                convert_from_camel(
                    self.visit_model()._meta.object_name)).appointment
        except AttributeError:
            appointment = cleaned_data.get('appointment')
        try:
            self.instance.check_time_point_status(
                appointment,
                exception_cls=forms.ValidationError)
        except AttributeError:
            pass
        # get the helper class
        consent_helper_cls = self._meta.model().get_consent_helper_cls()
        # check if consented to complete this form
        consent_helper_cls((self._meta.model, cleaned_data),
                           forms.ValidationError).is_consented_for_subject_instance()
        # Validates fields under edc_consent version control and other checks.
        consent_helper_cls((self._meta.model, cleaned_data),
                           forms.ValidationError).validate_versioned_fields()
        # validate that the off study form has not been entered with an off
        # study date less that or equal to report_datetime
        consent_helper_cls(
            (self._meta.model, cleaned_data), forms.ValidationError).is_off_study()
        return super(BaseConsentedModelForm, self).clean()
